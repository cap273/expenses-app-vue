from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import select, case, text
from sqlalchemy.sql import null
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
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
    try:
        data = request.json
        expenses = data["expenses"]
        counter = 0
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        # Get user's personal scope
        personal_scope = (
            db.session.query(Scope)
            .join(ScopeAccess)
            .filter(
                ScopeAccess.AccountID == current_user.id,
                Scope.ScopeType == 'personal',
                ScopeAccess.InviteStatus == 'accepted'
            )
            .first()
        )

        if not personal_scope:
            return jsonify({
                "success": False,
                "error": "No personal scope found for user"
            })

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
                            expense_date = datetime.strptime(
                                f"{year}-{month}-{day}", "%Y-%B-%d"
                            ).date()
                        except ValueError:
                            return jsonify({
                                "success": False,
                                "error": f"Invalid date: {day}-{month}-{year}",
                            })

                        # By default, use personal scope
                        scope_id = personal_scope.ScopeID

                        # If a household scope is specified, verify access
                        if scope != "personal":
                            scope_access = ScopeAccess.query.filter_by(
                                ScopeID=scope,
                                AccountID=current_user.id,
                                InviteStatus='accepted'
                            ).first()
                            if scope_access:
                                scope_id = scope

                        conn.execute(
                            expenses_table.insert().values(
                                ScopeID=scope_id,
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