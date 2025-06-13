from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import select, case, text, or_, and_
from sqlalchemy.sql import null
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, date
from dateutil import parser
from flask_login import current_user
from werkzeug.exceptions import BadRequestKeyError

from flask_backend.utils.db_tools import get_categories
from flask_backend.utils.session import login_required_api
from flask_backend.utils.category_mapping import get_category_for_transaction, is_income_category
from flask_backend.database.models import db, Account, Person, Scope, ScopeAccess
from flask_backend.database.tables import (
    expenses_table,
    categories_table,
    persons_table,
    scopes_table,
    scope_access_table,
    category_targets_table,
)

expense_routes = Blueprint("expense_routes", __name__)

@expense_routes.route("/api/get_expenses", methods=["GET"])
@login_required_api
def get_expenses():
    try:
        # First get all scope IDs the user has access to
        scope_query = (
            db.session.query(ScopeAccess.ScopeID)
            .filter(
                ScopeAccess.AccountID == current_user.id,
                ScopeAccess.InviteStatus == 'accepted'
            )
        )
        accessible_scope_ids = [result[0] for result in scope_query.all()]

        # Create a conditional expression for PersonName
        person_name_expr = case(
            (expenses_table.c.PersonID == null(), "Joint"), 
            else_=persons_table.c.PersonName
        ).label("PersonName")

        # Create a SQL query to select expenses and join with the persons table
        query = (
            select(
                expenses_table.c.ExpenseID,
                expenses_table.c.ExpenseDate,
                expenses_table.c.Amount,
                expenses_table.c.ExpenseCategory,
                expenses_table.c.AdditionalNotes,
                expenses_table.c.Currency,
                expenses_table.c.ScopeID,
                scopes_table.c.ScopeName,  # Add ScopeName
                scopes_table.c.ScopeType,  # Add ScopeType
                person_name_expr,
                # Plaid-related fields
                expenses_table.c.PlaidAccountID,
                expenses_table.c.PlaidTransactionID,
                expenses_table.c.MerchantName,
                expenses_table.c.SourceType,
                expenses_table.c.PlaidMerchantName,
                expenses_table.c.PlaidName,
                expenses_table.c.PlaidMerchantLogoURL,
                expenses_table.c.CategoryConfirmed,
                expenses_table.c.PlaidPersonalFinanceCategoryPrimary,
                expenses_table.c.IsIncome
            )
            .select_from(
                expenses_table.join(
                    persons_table,
                    expenses_table.c.PersonID == persons_table.c.PersonID,
                    isouter=True,
                ).join(
                scopes_table,  # Join with scopes table to get ScopeName and ScopeType
                expenses_table.c.ScopeID == scopes_table.c.ScopeID
                )
            )
            .where(expenses_table.c.ScopeID.in_(accessible_scope_ids))
        )

        # Execute the query using SQLAlchemy Core
        with current_app.config["ENGINE"].connect() as connection:
            result = connection.execute(query)
            user_expenses = result.fetchall()

        # Convert raw results to a list of dicts with split date
        expenses = []
        for row in user_expenses:
            expense_dict = row._asdict()
            
            # Handle possible None values for ExpenseDate
            if row.ExpenseDate is not None:
                expense_dict["Day"] = row.ExpenseDate.day
                expense_dict["Month"] = row.ExpenseDate.strftime("%B")
                expense_dict["Year"] = row.ExpenseDate.year
            else:
                # Add default values for null dates
                expense_dict["Day"] = None
                expense_dict["Month"] = None
                expense_dict["Year"] = None
            
            expenses.append(expense_dict)

        # Format the amount in each expense
        for expense in expenses:
            if expense["Currency"] == "USD":
                expense["Amount"] = "${:,.2f}".format(expense["Amount"])
            elif expense["Currency"] == "EUR":
                expense["Amount"] = "€{:,.2f}".format(expense["Amount"])
            # IsIncome is now directly from database, no need for manual logic

        return jsonify({"success": True, "expenses": expenses})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@expense_routes.route("/api/submit_expenses", methods=["POST"])
@login_required_api
def submit_new_expenses():
    with current_app.config["ENGINE"].connect() as connection:
        result = connection.execute(text("SELECT SYSDATETIMEOFFSET()"))
        server_time = result.scalar()
        print(f"DEBUG - SQL Server time: {server_time}")

    try:
        data = request.json
        expenses = data["expenses"]
        counter = 0
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        # Get all scopes the user has access to
        accessible_scopes = (
            db.session.query(ScopeAccess)
            .filter(
                ScopeAccess.AccountID == current_user.id,
                ScopeAccess.InviteStatus == 'accepted'
            )
            .all()
        )

        accessible_scope_ids = [scope.ScopeID for scope in accessible_scopes]

        try:
            with current_app.config["ENGINE"].connect() as conn:
                for expense in expenses:
                    try:
                        # Extract individual fields from the expense dictionary
                        scope = expense.get("scope")
                        day = expense.get("day")
                        month = expense.get("month")
                        year = expense.get("year")
                        amount = expense.get("amount")
                        category = expense.get("category")
                        merchant = expense.get("merchant", "")
                        notes = expense.get("notes")

                        # Validation
                        if not all([scope, day, month, year, amount, category]):
                            return jsonify({
                                "success": False,
                                "error": "Missing required fields in the expense data",
                            })

                        # Verify scope access
                        if scope not in accessible_scope_ids:
                            return jsonify({
                                "success": False,
                                "error": "Invalid or inaccessible scope",
                            })

                        # Date validation
                        try:
                            day = int(day)
                            year = int(year)
                            if not (1 <= day <= 31):
                                return jsonify({
                                    "success": False,
                                    "error": "Day must be between 1 and 31",
                                })
                            if not (2000 <= year <= 2050):
                                return jsonify({
                                    "success": False,
                                    "error": "Year must be between 2000 and 2050",
                                })
                        except ValueError:
                            return jsonify({
                                "success": False,
                                "error": "Day and Year must be integers",
                            })

                        if month not in months:
                            return jsonify({
                                "success": False,
                                "error": "Invalid month selected"
                            })

                        # Parse the date
                        try:
                            # Get month number (1-12) from month name
                            month_num = [i for i, m in enumerate(months, 1) if m == month][0]
                            expense_date = date(year, month_num, day)
                            print(f"DEBUG - Date being inserted: {expense_date}")
                        except (ValueError, IndexError):
                            return jsonify({
                                "success": False,
                                "error": f"Invalid date: {day}-{month}-{year}",
                            })

                        # Determine if this is an income transaction
                        is_income = is_income_category(category)
                        
                        conn.execute(
                            expenses_table.insert().values(
                                ScopeID=scope,  # Use the scope ID directly
                                PersonID=None,  # You might want to modify this based on your needs
                                Day=day,
                                Month=month,
                                Year=year,
                                ExpenseDate=expense_date,
                                Amount=float(amount.replace(",", "")),
                                ExpenseCategory=category,
                                MerchantName=merchant,
                                SourceType="manual",
                                AdditionalNotes=notes,
                                Currency=current_user.currency,
                                CreateDate=datetime.now().date(),
                                LastUpdated=datetime.now().date(),
                                CategoryConfirmed=True,  # Manual entries are pre-confirmed by user
                                IsIncome=is_income
                            )
                        )

                        counter += 1

                    except Exception as e:
                        return jsonify({"success": False, "error": str(e)})

                # Commit all the changes to the database
                conn.commit()

                return jsonify({
                    "success": True,
                    "message": f"{counter} expense{'s' if counter != 1 else ''} successfully recorded.",
                })

        except SQLAlchemyError as e:
            if current_app.config["FLASK_ENV"] == "development":
                print(e)
            return jsonify({"success": False, "error": "Database error"})

    except BadRequestKeyError:
        return jsonify({"success": False, "error": "Invalid request"})
    

@expense_routes.route("/api/submit_plaid_transactions", methods=["POST"])
@login_required_api
def submit_plaid_transactions():
    """
    This endpoint accepts a JSON payload with Plaid transactions and saves
    them into the SQL Server expenses table without duplicating records.
    
    Expected JSON format:
    {
        "scope": <scope_id>,
        "plaid_transactions": [
            {
                "account_id": "5krA3ABBJdcV1LARAoP1Iw9en5vRzBi5Xryy6",
                "transaction_id": "DJMkpkLL4gIdaNbEbkKaC7yNxQyEAlF3GNK3V",
                "transaction_type": "place",
                "category_id": "13005000",
                "authorized_date": "Fri, 15 Nov 2024 00:00:00 GMT",
                "date": "Sat, 16 Nov 2024 00:00:00 GMT",
                "amount": 89.4,
                "iso_currency_code": "USD",
                "logo_url": "https://plaid-category-icons.plaid.com/PFC_ENTERTAINMENT.png",
                "merchant_entity_id": null,
                "merchant_name": "FUN",
                "name": "SparkFun",
                "pending": false,
                "pending_transaction_id": null,
                "personal_finance_category": {
                    "confidence_level": "LOW",
                    "detailed": "ENTERTAINMENT_SPORTING_EVENTS_AMUSEMENT_PARKS_AND_MUSEUMS",
                    "primary": "ENTERTAINMENT"
                },
                "personal_finance_category_icon_url": "https://plaid-category-icons.plaid.com/PFC_ENTERTAINMENT.png"
            },
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        plaid_transactions = data.get("plaid_transactions")
        scope = data.get("scope")  # Required to associate the expense with a scope

        if not plaid_transactions or scope is None:
            return jsonify({
                "success": False,
                "error": "Missing required fields: 'scope' or 'plaid_transactions'"
            }), 400

        counter_inserted = 0
        counter_skipped = 0

        # Open a connection
        with current_app.config["ENGINE"].connect() as conn:
            # Build a list of unique (account_id, transaction_id) pairs from incoming transactions
            transaction_keys = [
                (txn.get("account_id"), txn.get("transaction_id"))
                for txn in plaid_transactions
                if txn.get("account_id") and txn.get("transaction_id")
            ]

            # Execute a single query to find any existing records matching these key pairs
            # Build a list of conditions for each (PlaidAccountID, PlaidTransactionID) pair.
            conditions = [
                and_(
                    expenses_table.c.PlaidAccountID == account_id,
                    expenses_table.c.PlaidTransactionID == transaction_id
                )
                for account_id, transaction_id in transaction_keys
            ]

            # Only add the WHERE clause if there is at least one condition
            if conditions:
                existing_rows = conn.execute(
                    expenses_table.select().where(or_(*conditions))
                ).fetchall()
            else:
                existing_rows = []

            # Create a set of keys for quick lookup
            existing_keys = {
                (row.PlaidAccountID, row.PlaidTransactionID) for row in existing_rows
            }

            # Prepare a list of new transaction records to insert
            values_to_insert = []

            for txn in plaid_transactions:
                key = (txn.get("account_id"), txn.get("transaction_id"))
                if key in existing_keys:
                    counter_skipped += 1
                    continue

                # Parse dates using dateutil.parser for flexibility
                try:
                    authorized_date_str = txn.get("authorized_date")
                    plaid_authorized_date = parser.parse(authorized_date_str).date() if authorized_date_str else None
                except Exception:
                    plaid_authorized_date = None

                try:
                    date_str = txn.get("date")
                    plaid_date = parser.parse(date_str).date() if date_str else None
                except Exception:
                    plaid_date = None

                # Determine date components from the parsed date (if available)
                # Make sure we always have a valid date
                if plaid_date:
                    day = plaid_date.day
                    month = plaid_date.strftime("%B")  # e.g., "November"
                    year = plaid_date.year
                    expense_date = plaid_date
                    expense_day_of_week = plaid_date.strftime("%A")
                else:
                    # Default to today's date if no date is provided
                    today = datetime.now().date()
                    day = today.day
                    month = today.strftime("%B")
                    year = today.year
                    expense_date = today
                    expense_day_of_week = today.strftime("%A")
                
                # adding category helper
                category=get_category_for_transaction(txn)
                # Build a dictionary of values for insertion
                record = {
                    "ScopeID": scope,
                    "PersonID": None,  # Adjust if tying to a specific user
                    "Day": day,
                    "Month": month,
                    "Year": year,
                    "ExpenseDate": expense_date,
                    "ExpenseDayOfWeek": expense_day_of_week,
                    "Amount": txn.get("amount"),
                    "AdjustedAmount": txn.get("amount"),  # Initially the same as Amount
                    "ExpenseCategory": category,  # Can be updated later (updated by janusz eventually)
                    "MerchantName": txn.get("merchant_name"),
                    "SourceType": "plaid",
                    "AdditionalNotes": None,
                    "CreateDate": datetime.now().date(),
                    "LastUpdated": datetime.now().date(),
                    "Currency": txn.get("iso_currency_code"),
                    "SuggestedCategory": None,
                    "CategoryConfirmed": False,

                    # Plaid-specific fields
                    "PlaidAccountID": txn.get("account_id"),
                    "PlaidTransactionID": txn.get("transaction_id"),
                    "PlaidTransactionType": txn.get("transaction_type"),
                    "PlaidCategoryID": txn.get("category_id"),
                    "PlaidAuthorizedDate": plaid_authorized_date,
                    "PlaidDate": plaid_date,
                    "PlaidAmount": txn.get("amount"),
                    "PlaidCurrencyCode": txn.get("iso_currency_code"),
                    "PlaidMerchantLogoURL": txn.get("logo_url"),
                    "PlaidMerchantEntityID": txn.get("merchant_entity_id"),
                    "PlaidMerchantName": txn.get("merchant_name"),
                    "PlaidName": txn.get("name"),
                    "PlaidPending": txn.get("pending"),
                    "PlaidPendingTransactionID": txn.get("pending_transaction_id"),
                    "PlaidPersonalFinanceCategoryConfidence": txn.get("personal_finance_category", {}).get("confidence_level"),
                    "PlaidPersonalFinanceCategoryDetailed": txn.get("personal_finance_category", {}).get("detailed"),
                    "PlaidPersonalFinanceCategoryPrimary": txn.get("personal_finance_category", {}).get("primary"),
                    "PlaidPersonalFinanceCategoryIconURL": txn.get("personal_finance_category_icon_url"),
                }
                values_to_insert.append(record)
                counter_inserted += 1

            # Execute a bulk insert for all new records
            if values_to_insert:
                conn.execute(expenses_table.insert(), values_to_insert)
            conn.commit()

        return jsonify({
            "success": True,
            "message": (
                f"{counter_inserted} new transaction{'s' if counter_inserted != 1 else ''} recorded. "
                f"{counter_skipped} duplicate transaction{'s' if counter_skipped != 1 else ''} skipped."
            )
        })

    except SQLAlchemyError as db_err:
        current_app.logger.error(db_err)
        return jsonify({"success": False, "error": "Database error"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@expense_routes.route("/api/delete_expenses", methods=["POST"])
@login_required_api
def delete_expenses():
    try:
        data = request.json
        expense_ids = data.get("expenseIds", [])

        if not expense_ids:
            return jsonify({"success": False, "message": "No expense IDs provided."})

        # Get user's accessible scope IDs
        scope_query = (
            db.session.query(ScopeAccess.ScopeID)
            .filter(
                ScopeAccess.AccountID == current_user.id,
                ScopeAccess.InviteStatus == 'accepted'
            )
        )
        accessible_scope_ids = [result[0] for result in scope_query.all()]

        with current_app.config["ENGINE"].connect() as connection:
            # Delete expenses only if they belong to user's accessible scopes
            delete_statement = expenses_table.delete().where(
                expenses_table.c.ExpenseID.in_(expense_ids),
                expenses_table.c.ScopeID.in_(accessible_scope_ids)
            )
            result = connection.execute(delete_statement)

            if result.rowcount == 0:
                return jsonify({
                    "success": False,
                    "message": "No expenses were deleted, possible invalid ExpenseIDs or insufficient permissions."
                })

            connection.commit()

        return jsonify({"success": True, "message": "Expenses deleted successfully."})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@expense_routes.route("/api/update_expense", methods=["PUT"])
@login_required_api
def update_expense():
    try:
        data = request.json
        expenses = data.get("expenses", [])

        if not expenses:
            return jsonify({"success": False, "error": "No expense data provided."})

        # Get user's accessible scope IDs
        scope_query = (
            db.session.query(ScopeAccess.ScopeID)
            .filter(
                ScopeAccess.AccountID == current_user.id,
                ScopeAccess.InviteStatus == 'accepted'
            )
        )
        accessible_scope_ids = [result[0] for result in scope_query.all()]

        expense = expenses[0]  # Assuming only one expense is edited at a time
        expense_id = expense.get("ExpenseID")

        if not expense_id:
            return jsonify({"success": False, "error": "ExpenseID is required for updating."})

        # Extract and validate data as before...
        scope = expense.get("scope")
        day = expense.get("day")
        month = expense.get("month")
        year = expense.get("year")
        amount = expense.get("amount")
        category = expense.get("category")
        merchant = expense.get("merchant", "")
        notes = expense.get("notes")

        expense_date = datetime.strptime(f"{year}-{month}-{day}", "%Y-%B-%d").date()
        
        # Determine if this is an income transaction
        is_income = is_income_category(category)

        with current_app.config["ENGINE"].connect() as conn:
            update_stmt = (
                expenses_table.update()
                .where(
                    expenses_table.c.ExpenseID == expense_id,
                    expenses_table.c.ScopeID.in_(accessible_scope_ids)
                )
                .values(
                    Day=day,
                    Month=month,
                    Year=year,
                    ExpenseDate=expense_date,
                    Amount=float(amount.replace(",", "")),
                    ExpenseCategory=category,
                    MerchantName=merchant,
                    AdditionalNotes=notes,
                    LastUpdated=datetime.now().date(),
                    CategoryConfirmed=True,  # Set to True when manually edited
                    IsIncome=is_income
                )
            )
            result = conn.execute(update_stmt)
            conn.commit()

            if result.rowcount == 0:
                return jsonify({"success": False, "error": "Expense not found or not authorized."})

        return jsonify({"success": True, "message": "Expense updated successfully."})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@expense_routes.route("/api/get_categories", methods=["GET"])
@login_required_api
def get_categories_api():
    # Fetch and return all the (default) expense categories
    categories = get_categories(current_app.config["ENGINE"], categories_table)
    return jsonify({"categories": categories})


# Add this new endpoint to flask_backend/routes/expense_routes.py

@expense_routes.route("/api/bulk_update_expenses", methods=["POST"])
@login_required_api
def bulk_update_expenses():
    try:
        data = request.json
        expense_ids = data.get("expenseIds", [])
        updates = data.get("updates", {})

        if not expense_ids:
            return jsonify({"success": False, "message": "No expense IDs provided."})
        
        if not updates:
            return jsonify({"success": False, "message": "No updates provided."})

        # Get user's accessible scope IDs
        scope_query = (
            db.session.query(ScopeAccess.ScopeID)
            .filter(
                ScopeAccess.AccountID == current_user.id,
                ScopeAccess.InviteStatus == 'accepted'
            )
        )
        accessible_scope_ids = [result[0] for result in scope_query.all()]

        # Prepare the update values
        update_values = {}
        
        # Update category if provided
        if 'category' in updates:
            update_values['ExpenseCategory'] = updates['category']
            update_values['CategoryConfirmed'] = True
            # Determine if this is an income transaction
            update_values['IsIncome'] = is_income_category(updates['category'])
        # Update scope if provided
        if 'scope' in updates:
            # Verify the scope is accessible to the user
            if int(updates['scope']) not in accessible_scope_ids:
                return jsonify({
                    "success": False, 
                    "message": "You don't have access to the selected scope."
                })
            update_values['ScopeID'] = updates['scope']
        
        # Update date if all date components are provided
        if all(key in updates for key in ['day', 'month', 'year']):
            try:
                # Validate and parse the date
                day = int(updates['day'])
                month = updates['month']
                year = int(updates['year'])
                
                if not (1 <= day <= 31):
                    return jsonify({
                        "success": False,
                        "message": "Day must be between 1 and 31"
                    })
                
                if not (2000 <= year <= 2050):
                    return jsonify({
                        "success": False,
                        "message": "Year must be between 2000 and 2050"
                    })
                
                months = [
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ]
                
                if month not in months:
                    return jsonify({
                        "success": False,
                        "message": "Invalid month"
                    })
                
                # Get month number (1-12) from month name
                month_num = [i for i, m in enumerate(months, 1) if m == month][0]
                
                # Create a date object
                expense_date = datetime(year, month_num, day).date()
                
                # Update date fields
                update_values['Day'] = day
                update_values['Month'] = month
                update_values['Year'] = year
                update_values['ExpenseDate'] = expense_date
                
                # Update day of week
                update_values['ExpenseDayOfWeek'] = expense_date.strftime('%A')
                
            except (ValueError, IndexError) as e:
                return jsonify({
                    "success": False,
                    "message": f"Invalid date: {str(e)}"
                })
        
        # Update notes if provided
        if 'notes' in updates:
            update_values['AdditionalNotes'] = updates['notes']
        
        # Set the last updated date
        update_values['LastUpdated'] = datetime.now().date()
        
        # Perform the bulk update
        with current_app.config["ENGINE"].connect() as conn:
            # First, make sure all expenses belong to accessible scopes
            # New style (SQLAlchemy 1.4+):
            check_query = select(expenses_table.c.ExpenseID).where(
                and_(
                    expenses_table.c.ExpenseID.in_(expense_ids),
                    expenses_table.c.ScopeID.in_(accessible_scope_ids)
                )
            )
            result = conn.execute(check_query)
            valid_expense_ids = [row[0] for row in result]
            
            # Identify any expense IDs that don't belong to the user
            invalid_ids = set(expense_ids) - set(valid_expense_ids)
            if invalid_ids:
                return jsonify({
                    "success": False,
                    "message": f"You don't have permission to update {len(invalid_ids)} expenses."
                })
            
            # Update the valid expenses
            update_stmt = expenses_table.update().where(
                expenses_table.c.ExpenseID.in_(valid_expense_ids)
            ).values(**update_values)
            
            result = conn.execute(update_stmt)
            conn.commit()
            
            return jsonify({
                "success": True,
                "message": f"Successfully updated {result.rowcount} expenses."
            })
            
    except Exception as e:
        print(f"Error in bulk update: {str(e)}")
        return jsonify({"success": False, "message": str(e)})

@expense_routes.route("/api/get_category_averages", methods=["GET"])
@login_required_api
def get_category_averages():
    """
    Calculate 12-month category averages for the user's accessible scopes
    """
    try:
        # Get user's accessible scope IDs
        scope_query = (
            db.session.query(ScopeAccess.ScopeID)
            .filter(
                ScopeAccess.AccountID == current_user.id,
                ScopeAccess.InviteStatus == 'accepted'
            )
        )
        accessible_scope_ids = [result[0] for result in scope_query.all()]

        if not accessible_scope_ids:
            return jsonify({"success": True, "averages": []})

        # Calculate 12 months ago from now
        from datetime import datetime, timedelta
        from dateutil.relativedelta import relativedelta
        
        end_date = datetime.now().date()
        start_date = end_date - relativedelta(months=12)

        with current_app.config["ENGINE"].connect() as connection:
            # Query expenses from the last 12 months, excluding income
            query = (
                select(
                    expenses_table.c.ExpenseCategory,
                    expenses_table.c.Amount
                )
                .where(
                    and_(
                        expenses_table.c.ScopeID.in_(accessible_scope_ids),
                        expenses_table.c.ExpenseDate >= start_date,
                        expenses_table.c.ExpenseDate <= end_date,
                        expenses_table.c.IsIncome != True,  # Exclude income
                        expenses_table.c.ExpenseCategory.isnot(None)  # Exclude null categories
                    )
                )
            )
            
            result = connection.execute(query)
            expenses = result.fetchall()

        # Calculate category totals and count months with transactions
        category_totals = {}
        months_with_transactions = set()
        
        for expense in expenses:
            category = expense.ExpenseCategory
            amount = expense.Amount
            # Track which months had transactions
            expense_month = (expense.ExpenseDate.year, expense.ExpenseDate.month)
            months_with_transactions.add(expense_month)
            
            if category in category_totals:
                category_totals[category] += amount
            else:
                category_totals[category] = amount

        # Calculate actual months with activity (minimum 1 to avoid division by zero)
        active_months = max(len(months_with_transactions), 1)
        
        # Calculate monthly averages based on active months only
        category_averages = []
        for category, total in category_totals.items():
            monthly_average = total / active_months
            category_averages.append({
                "category": category,
                "monthly_average": round(monthly_average, 2),
                "total_12_months": round(total, 2),
                "active_months": active_months
            })

        # Sort by monthly average (descending) and take top 10
        category_averages.sort(key=lambda x: x["monthly_average"], reverse=True)
        top_categories = category_averages[:10]

        return jsonify({
            "success": True,
            "averages": top_categories,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "active_months": active_months,
                "total_months_in_period": 12
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@expense_routes.route("/api/get_category_targets", methods=["GET"])
@login_required_api
def get_category_targets():
    """
    Get user's category targets for accessible scopes
    """
    try:
        # Get user's accessible scope IDs
        scope_query = (
            db.session.query(ScopeAccess.ScopeID)
            .filter(
                ScopeAccess.AccountID == current_user.id,
                ScopeAccess.InviteStatus == 'accepted'
            )
        )
        accessible_scope_ids = [result[0] for result in scope_query.all()]

        with current_app.config["ENGINE"].connect() as connection:
            query = (
                select(
                    category_targets_table.c.TargetID,
                    category_targets_table.c.ScopeID,
                    category_targets_table.c.CategoryName,
                    category_targets_table.c.MonthlyTarget,
                    category_targets_table.c.IsActive
                )
                .where(
                    and_(
                        category_targets_table.c.AccountID == current_user.id,
                        category_targets_table.c.ScopeID.in_(accessible_scope_ids),
                        category_targets_table.c.IsActive == True
                    )
                )
            )
            
            result = connection.execute(query)
            targets = result.fetchall()

        targets_list = []
        for target in targets:
            targets_list.append({
                "target_id": target.TargetID,
                "scope_id": target.ScopeID,
                "category": target.CategoryName,
                "monthly_target": target.MonthlyTarget
            })

        return jsonify({"success": True, "targets": targets_list})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@expense_routes.route("/api/save_category_targets", methods=["POST"])
@login_required_api
def save_category_targets():
    """
    Save or update category targets for the user
    """
    try:
        data = request.json
        targets = data.get("targets", [])
        
        if not targets:
            return jsonify({"success": False, "error": "No targets provided"})

        # Get user's accessible scope IDs
        scope_query = (
            db.session.query(ScopeAccess.ScopeID)
            .filter(
                ScopeAccess.AccountID == current_user.id,
                ScopeAccess.InviteStatus == 'accepted'
            )
        )
        accessible_scope_ids = [result[0] for result in scope_query.all()]

        with current_app.config["ENGINE"].connect() as connection:
            # First, deactivate all existing targets for the user
            deactivate_stmt = (
                category_targets_table.update()
                .where(
                    and_(
                        category_targets_table.c.AccountID == current_user.id,
                        category_targets_table.c.ScopeID.in_(accessible_scope_ids)
                    )
                )
                .values(IsActive=False, LastUpdated=datetime.now().date())
            )
            connection.execute(deactivate_stmt)

            # Insert new targets
            for target in targets:
                category = target.get("category")
                monthly_target = target.get("monthly_target")
                scope_id = target.get("scope_id")

                if not all([category, monthly_target is not None, scope_id]):
                    continue

                # Verify scope access
                if scope_id not in accessible_scope_ids:
                    continue

                connection.execute(
                    category_targets_table.insert().values(
                        ScopeID=scope_id,
                        AccountID=current_user.id,
                        CategoryName=category,
                        MonthlyTarget=float(monthly_target),
                        IsActive=True,
                        CreateDate=datetime.now().date(),
                        LastUpdated=datetime.now().date()
                    )
                )

            connection.commit()

        return jsonify({"success": True, "message": "Category targets saved successfully"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@expense_routes.route("/api/get_category_progress", methods=["GET"])
@login_required_api
def get_category_progress():
    """
    Get current month progress for each category target
    """
    try:
        # Get user's accessible scope IDs
        scope_query = (
            db.session.query(ScopeAccess.ScopeID)
            .filter(
                ScopeAccess.AccountID == current_user.id,
                ScopeAccess.InviteStatus == 'accepted'
            )
        )
        accessible_scope_ids = [result[0] for result in scope_query.all()]

        # Get current month boundaries
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        
        with current_app.config["ENGINE"].connect() as connection:
            # Get active targets
            targets_query = (
                select(
                    category_targets_table.c.TargetID,
                    category_targets_table.c.ScopeID,
                    category_targets_table.c.CategoryName,
                    category_targets_table.c.MonthlyTarget
                )
                .where(
                    and_(
                        category_targets_table.c.AccountID == current_user.id,
                        category_targets_table.c.ScopeID.in_(accessible_scope_ids),
                        category_targets_table.c.IsActive == True
                    )
                )
            )
            
            targets_result = connection.execute(targets_query)
            targets = targets_result.fetchall()

            if not targets:
                return jsonify({"success": True, "progress": []})

            # Get current month spending for each category
            from datetime import date
            month_start = date(current_year, current_month, 1)
            if current_month == 12:
                month_end = date(current_year + 1, 1, 1)
            else:
                month_end = date(current_year, current_month + 1, 1)
            
            expenses_query = (
                select(
                    expenses_table.c.ExpenseCategory,
                    expenses_table.c.Amount,
                    expenses_table.c.ScopeID
                )
                .where(
                    and_(
                        expenses_table.c.ScopeID.in_(accessible_scope_ids),
                        expenses_table.c.ExpenseDate >= month_start,
                        expenses_table.c.ExpenseDate < month_end,
                        expenses_table.c.IsIncome != True
                    )
                )
            )
            
            expenses_result = connection.execute(expenses_query)
            expenses = expenses_result.fetchall()

        # Calculate current spending by category and scope
        current_spending = {}
        for expense in expenses:
            key = (expense.ExpenseCategory, expense.ScopeID)
            if key in current_spending:
                current_spending[key] += expense.Amount
            else:
                current_spending[key] = expense.Amount

        # Build progress data
        progress_data = []
        target_categories = set()
        everything_else_target = None
        
        for target in targets:
            if target.CategoryName == "Everything Else":
                everything_else_target = target
                continue  # Don't add "Everything Else" to regular targets here
                
            key = (target.CategoryName, target.ScopeID)
            current_spent = current_spending.get(key, 0)
            progress_percentage = (current_spent / target.MonthlyTarget * 100) if target.MonthlyTarget > 0 else 0
            
            progress_data.append({
                "target_id": target.TargetID,
                "scope_id": target.ScopeID,
                "category": target.CategoryName,
                "monthly_target": target.MonthlyTarget,
                "current_spent": round(current_spent, 2),
                "progress_percentage": round(progress_percentage, 1),
                "remaining": round(target.MonthlyTarget - current_spent, 2),
                "is_over_budget": current_spent > target.MonthlyTarget
            })
            
            # Track categories that have targets (for all scopes)
            target_categories.add(target.CategoryName)

        # Calculate "Everything Else" spending
        everything_else_spent = 0
        for (category, scope_id), amount in current_spending.items():
            if category not in target_categories:
                everything_else_spent += amount

        # Always add "Everything Else" as a virtual category (even if $0)
        if everything_else_target:
            # If there's a target for "Everything Else", treat it like a normal category
            progress_percentage = (everything_else_spent / everything_else_target.MonthlyTarget * 100) if everything_else_target.MonthlyTarget > 0 else 0
            progress_data.append({
                "target_id": everything_else_target.TargetID,
                "scope_id": everything_else_target.ScopeID,
                "category": "Everything Else",
                "monthly_target": everything_else_target.MonthlyTarget,
                "current_spent": round(everything_else_spent, 2),
                "progress_percentage": round(progress_percentage, 1),
                "remaining": round(everything_else_target.MonthlyTarget - everything_else_spent, 2),
                "is_over_budget": everything_else_spent > everything_else_target.MonthlyTarget,
                "is_everything_else": True
            })
        else:
            # No target set for "Everything Else"
            progress_data.append({
                "target_id": None,
                "scope_id": None,
                "category": "Everything Else",
                "monthly_target": 0,
                "current_spent": round(everything_else_spent, 2),
                "progress_percentage": 0,
                "remaining": round(-everything_else_spent, 2),
                "is_over_budget": False,
                "is_everything_else": True
            })

        # Sort by progress percentage (descending), but put "Everything Else" at the end
        progress_data.sort(key=lambda x: (x.get("is_everything_else", False), -x["progress_percentage"]))

        return jsonify({
            "success": True,
            "progress": progress_data,
            "month": now.strftime("%B %Y")
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@expense_routes.route("/api/get_available_categories", methods=["GET"])
@login_required_api
def get_available_categories():
    """
    Get all categories that have been used in the user's expenses plus default categories
    """
    try:
        # Get user's accessible scope IDs
        scope_query = (
            db.session.query(ScopeAccess.ScopeID)
            .filter(
                ScopeAccess.AccountID == current_user.id,
                ScopeAccess.InviteStatus == 'accepted'
            )
        )
        accessible_scope_ids = [result[0] for result in scope_query.all()]

        categories_set = set()
        
        with current_app.config["ENGINE"].connect() as connection:
            # Get categories from user's expenses
            expenses_query = (
                select(expenses_table.c.ExpenseCategory)
                .where(
                    and_(
                        expenses_table.c.ScopeID.in_(accessible_scope_ids),
                        expenses_table.c.ExpenseCategory.isnot(None),
                        expenses_table.c.IsIncome != True
                    )
                )
                .distinct()
            )
            
            result = connection.execute(expenses_query)
            expense_categories = result.fetchall()
            
            for row in expense_categories:
                if row.ExpenseCategory:
                    categories_set.add(row.ExpenseCategory)
            
            # Get default categories from the categories table
            default_categories_query = select(categories_table.c.CategoryName)
            result = connection.execute(default_categories_query)
            default_categories = result.fetchall()
            
            for row in default_categories:
                categories_set.add(row.CategoryName)

        # Convert to sorted list
        categories_list = sorted(list(categories_set))
        
        # Add "Everything Else" as a special category option
        if "Everything Else" not in categories_list:
            categories_list.append("Everything Else")
        
        return jsonify({
            "success": True,
            "categories": categories_list
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@expense_routes.route("/api/get_spending_comparison", methods=["GET"])
@login_required_api
def get_spending_comparison():
    """
    Get current month spending compared to average monthly spending (prorated by date)
    """
    try:
        # Get user's accessible scope IDs
        scope_query = (
            db.session.query(ScopeAccess.ScopeID)
            .filter(
                ScopeAccess.AccountID == current_user.id,
                ScopeAccess.InviteStatus == 'accepted'
            )
        )
        accessible_scope_ids = [result[0] for result in scope_query.all()]

        if not accessible_scope_ids:
            return jsonify({"success": True, "comparison": None})

        from datetime import datetime, date
        from dateutil.relativedelta import relativedelta
        import calendar
        
        now = datetime.now()
        current_date = now.date()
        current_month = now.month
        current_year = now.year
        current_day = now.day
        
        # Get total days in current month
        days_in_month = calendar.monthrange(current_year, current_month)[1]
        
        # Calculate 12 months ago from now
        end_date = current_date
        start_date = end_date - relativedelta(months=12)

        with current_app.config["ENGINE"].connect() as connection:
            # Get current month spending
            current_month_query = (
                select(expenses_table.c.Amount)
                .where(
                    and_(
                        expenses_table.c.ScopeID.in_(accessible_scope_ids),
                        expenses_table.c.Month == now.strftime("%B"),
                        expenses_table.c.Year == current_year,
                        expenses_table.c.IsIncome != True
                    )
                )
            )
            
            current_result = connection.execute(current_month_query)
            current_expenses = current_result.fetchall()
            current_month_total = sum(expense.Amount for expense in current_expenses)
            
            # Get historical expenses for average calculation
            historical_query = (
                select(
                    expenses_table.c.Amount,
                    expenses_table.c.ExpenseDate
                )
                .where(
                    and_(
                        expenses_table.c.ScopeID.in_(accessible_scope_ids),
                        expenses_table.c.ExpenseDate >= start_date,
                        expenses_table.c.ExpenseDate <= end_date,
                        expenses_table.c.IsIncome != True
                    )
                )
            )
            
            historical_result = connection.execute(historical_query)
            historical_expenses = historical_result.fetchall()

        # Calculate monthly totals and count active months
        monthly_totals = {}
        months_with_transactions = set()
        
        for expense in historical_expenses:
            expense_month_key = (expense.ExpenseDate.year, expense.ExpenseDate.month)
            months_with_transactions.add(expense_month_key)
            
            if expense_month_key in monthly_totals:
                monthly_totals[expense_month_key] += expense.Amount
            else:
                monthly_totals[expense_month_key] = expense.Amount

        # Calculate average monthly spending (excluding current month if it's in the data)
        current_month_key = (current_year, current_month)
        if current_month_key in monthly_totals:
            # Remove current month from historical calculation
            del monthly_totals[current_month_key]
            months_with_transactions.discard(current_month_key)
        
        active_months = len(months_with_transactions)
        
        if active_months > 0:
            total_historical_spending = sum(monthly_totals.values())
            average_monthly_spending = total_historical_spending / active_months
            
            # Calculate prorated average for current date
            progress_through_month = current_day / days_in_month
            expected_spending_by_now = average_monthly_spending * progress_through_month
            
            # Calculate comparison metrics
            difference = current_month_total - expected_spending_by_now
            percentage_difference = (difference / expected_spending_by_now * 100) if expected_spending_by_now > 0 else 0
            
            # Projected month-end spending based on current pace
            if current_day > 0:
                daily_average = current_month_total / current_day
                projected_month_end = daily_average * days_in_month
            else:
                projected_month_end = 0
                
            comparison_data = {
                "current_month_total": round(current_month_total, 2),
                "average_monthly_spending": round(average_monthly_spending, 2),
                "expected_spending_by_now": round(expected_spending_by_now, 2),
                "difference": round(difference, 2),
                "percentage_difference": round(percentage_difference, 1),
                "projected_month_end": round(projected_month_end, 2),
                "current_day": current_day,
                "days_in_month": days_in_month,
                "progress_through_month": round(progress_through_month * 100, 1),
                "active_months": active_months,
                "month_name": now.strftime("%B"),
                "is_ahead": difference > 0,
                "is_behind": difference < 0
            }
        else:
            comparison_data = None

        return jsonify({
            "success": True,
            "comparison": comparison_data
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})