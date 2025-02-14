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
from flask_backend.database.models import db, Account, Person, Scope, ScopeAccess
from flask_backend.database.tables import (
    expenses_table,
    categories_table,
    persons_table,
    scopes_table,
    scope_access_table,
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
        expenses = [
            {
                **row._asdict(),
                "Day": row.ExpenseDate.day,
                "Month": row.ExpenseDate.strftime("%B"),
                "Year": row.ExpenseDate.year,
            }
            for row in user_expenses
        ]

        # Format the amount in each expense
        for expense in expenses:
            if expense["Currency"] == "USD":
                expense["Amount"] = "${:,.2f}".format(expense["Amount"])
            elif expense["Currency"] == "EUR":
                expense["Amount"] = "€{:,.2f}".format(expense["Amount"])

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
                                AdditionalNotes=notes,
                                Currency=current_user.currency,
                                CreateDate=datetime.now().date(),
                                LastUpdated=datetime.now().date()
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
                if plaid_date:
                    day = plaid_date.day
                    month = plaid_date.strftime("%B")  # e.g., "November"
                    year = plaid_date.year
                    expense_date = plaid_date
                    expense_day_of_week = plaid_date.strftime("%A")
                else:
                    day = month = year = expense_date = expense_day_of_week = None

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
                    "ExpenseCategory": None,  # Can be updated later
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
        notes = expense.get("notes")

        expense_date = datetime.strptime(f"{year}-{month}-{day}", "%Y-%B-%d").date()

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
                    AdditionalNotes=notes,
                    LastUpdated=datetime.now().date()
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