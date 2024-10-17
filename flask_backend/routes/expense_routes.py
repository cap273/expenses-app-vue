from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import select, case
from sqlalchemy.sql import null
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from flask_login import current_user
from werkzeug.exceptions import BadRequestKeyError

from flask_backend.utils.db_tools import get_categories
from flask_backend.utils.session import login_required_api
from flask_backend.database.models import db, Account, Person
from flask_backend.database.tables import (
    expenses_table,
    categories_table,
    persons_table,
)

expense_routes = Blueprint("expense_routes", __name__)


@expense_routes.route("/api/get_expenses", methods=["GET"])
@login_required_api
def get_expenses():
    # Create a conditional expression for PersonName
    person_name_expr = case(
        (expenses_table.c.PersonID == null(), "Joint"), else_=persons_table.c.PersonName
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
            person_name_expr,
        )
        .select_from(
            expenses_table.join(
                persons_table,
                expenses_table.c.PersonID == persons_table.c.PersonID,
                isouter=True,
            )
        )
        .where(expenses_table.c.AccountID == current_user.id)
    )

    # Execute the query using SQLAlchemy Core
    with current_app.config["ENGINE"].connect() as connection:
        result = connection.execute(query)
        user_expenses = result.fetchall()

    # Convert raw results to a list of dicts
    #expenses = [row._asdict() for row in user_expenses]
    #modified expenses to split out expense date based on form inptus
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


@expense_routes.route("/api/get_categories", methods=["GET"])
@login_required_api
def get_categories_api():
    # Fetch and return all the (default) expense categories
    categories = get_categories(current_app.config["ENGINE"], categories_table)
    return jsonify({"categories": categories})


@expense_routes.route("/api/submit_expenses", methods=["POST"])
@login_required_api
def submit_new_expenses():
    try:
        # Parse JSON data from request
        data = request.json
        expenses = data["expenses"]
        counter = 0
        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

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
                            return jsonify(
                                {
                                    "success": False,
                                    "error": "Missing required fields in the expense data",
                                }
                            )

                        try:
                            day = int(day)
                            year = int(year)
                            if not (1 <= day <= 31):
                                return jsonify(
                                    {
                                        "success": False,
                                        "error": "Day must be between 1 and 31",
                                    }
                                )
                            if not (2000 <= year <= 2050):
                                return jsonify(
                                    {
                                        "success": False,
                                        "error": "Year must be between 2000 and 2050",
                                    }
                                )
                        except ValueError:
                            return jsonify(
                                {
                                    "success": False,
                                    "error": "Day and Year must be integers",
                                }
                            )

                        if month not in months:
                            return jsonify(
                                {"success": False, "error": "Invalid month selected"}
                            )

                        # Try to parse the date
                        try:
                            expense_date = datetime.strptime(
                                f"{year}-{month}-{day}", "%Y-%B-%d"
                            ).date()
                        except ValueError:
                            # Handle invalid date
                            return jsonify(
                                {
                                    "success": False,
                                    "error": f"Invalid date: {day}-{month}-{year}",
                                }
                            )

                        # Determine if the scope is joint or individual
                        person_id = None if scope == "Joint" else scope
                        expense_scope = "Joint" if scope == "Joint" else "Individual"

                        # Validate that any person_id is associated with the current user's account
                        if person_id is not None:
                            person = Person.query.filter_by(
                                PersonID=person_id, AccountID=current_user.id
                            ).first()
                            if person is None:
                                return jsonify(
                                    {
                                        "success": False,
                                        "error": f"PersonID {person_id} is not associated with the current user's account.",
                                    }
                                )

                        conn.execute(
                            expenses_table.insert().values(
                                AccountID=current_user.id,
                                ExpenseScope=expense_scope,  # Set to Joint or Individual
                                PersonID=person_id,  # Set to None if Joint, otherwise set to PersonID
                                Day=day,
                                Month=month,
                                Year=year,
                                ExpenseDate=expense_date,
                                Amount=float(
                                    amount.replace(",", "")
                                ),  # Ensure no commas in submission from thousands separator
                                ExpenseCategory=category,
                                AdditionalNotes=notes,
                                Currency=current_user.currency,
                            )
                        )

                        counter += 1

                    except Exception as e:
                        return jsonify({"success": False, "error": str(e)})

                # Commit all the changes to the database
                conn.commit()

                return jsonify(
                    {
                        "success": True,
                        "message": f"{counter} expense{'s' if counter != 1 else ''} successfully recorded.",
                    }
                )

        except SQLAlchemyError as e:
            if current_app.config["FLASK_ENV"] == "development":
                print(e)
            return jsonify({"success": False, "error": "Database error"})

    except BadRequestKeyError:
        return jsonify({"success": False, "error": "Invalid request"})

#Delete expenses
@expense_routes.route("/api/delete_expenses", methods=["POST"])
@login_required_api
def delete_expenses():
    try:
        data = request.json
        expense_ids = data.get("expenseIds", [])

        # Log the received expense IDs for debugging
        print("Received expense IDs for deletion:", expense_ids)

        if not expense_ids:
            return jsonify({"success": False, "message": "No expense IDs provided."})

        with current_app.config["ENGINE"].connect() as connection:
            # Execute the delete statement
            delete_statement = expenses_table.delete().where(expenses_table.c.ExpenseID.in_(expense_ids))
            result = connection.execute(delete_statement)

            # Log the result of the deletion operation
            print(f"Deleted {result.rowcount} rows from expenses_table.")

            # If no rows were deleted, provide feedback
            if result.rowcount == 0:
                return jsonify({"success": False, "message": "No expenses were deleted, possible invalid ExpenseIDs."})

            # Explicit commit to make sure the changes persist
            connection.commit()

        return jsonify({"success": True, "message": "Expenses deleted successfully."})

    except Exception as e:
        # Log the error if something went wrong
        print(f"Error during deletion: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

#Update expenses
@expense_routes.route("/api/update_expense", methods=["PUT"])
@login_required_api
def update_expense():
    try:
        data = request.json
        expenses = data.get("expenses", [])

        if not expenses:
            return jsonify({"success": False, "error": "No expense data provided."})

        expense = expenses[0]  # Assuming only one expense is edited at a time
        expense_id = expense.get("ExpenseID")

        if not expense_id:
            return jsonify({"success": False, "error": "ExpenseID is required for updating."})

        # Validate and extract data
        # ... (same validation as in submit_new_expenses)

        # Extract individual fields from the expense dictionary
        scope = expense.get("scope")
        day = expense.get("day")
        month = expense.get("month")
        year = expense.get("year")
        amount = expense.get("amount")
        category = expense.get("category")
        notes = expense.get("notes")

        # ... (rest of validation)

        # Prepare data for update
        expense_date = datetime.strptime(f"{year}-{month}-{day}", "%Y-%B-%d").date()
        person_id = None if scope == "Joint" else scope
        expense_scope = "Joint" if scope == "Joint" else "Individual"

        with current_app.config["ENGINE"].connect() as conn:
            update_stmt = (
                expenses_table.update()
                .where(
                    expenses_table.c.ExpenseID == expense_id,
                    expenses_table.c.AccountID == current_user.id,
                )
                .values(
                    ExpenseScope=expense_scope,
                    PersonID=person_id,
                    Day=day,
                    Month=month,
                    Year=year,
                    ExpenseDate=expense_date,
                    Amount=float(amount.replace(",", "")),
                    ExpenseCategory=category,
                    AdditionalNotes=notes,
                )
            )
            result = conn.execute(update_stmt)
            conn.commit()

            if result.rowcount == 0:
                return jsonify({"success": False, "error": "Expense not found or not authorized."})

        return jsonify({"success": True, "message": "Expense updated successfully."})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
