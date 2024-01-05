from flask import Flask, request, jsonify, send_from_directory
from sqlalchemy import create_engine, select, case
from sqlalchemy.sql import null
from sqlalchemy.exc import SQLAlchemyError
import os
import json
from dotenv import load_dotenv
import logging
from datetime import datetime
from flask_login import (
    LoginManager,
    login_required,
    logout_user,
    current_user,
)
from urllib.parse import urlparse
from werkzeug.exceptions import BadRequestKeyError

from flask_backend.utils.db_tools import populate_categories_table, get_categories, get_database_url
from flask_backend.utils.session import login_and_update_last_login, login_required_api
from flask_backend.database.models import db, Account, Person
from flask_backend.database.tables import (
    expenses_table,
    categories_table,
    persons_table,
    CATEGORY_LIST,
)

# Load environment variables from .env file
load_dotenv()

# Retrieve database credentials from environment variables
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")
FLASK_ENV = os.getenv("FLASK_ENV")

# Configure logging based on the environment
if FLASK_ENV == "development":
    logging.basicConfig()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.WARNING)

DATABASE_URL = get_database_url(DB_USERNAME, DB_PASSWORD, DB_SERVER, DB_NAME)

app = Flask(__name__, static_folder='./vue-frontend/dist', static_url_path='/')

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY"
)  # Set the secret key to use for Flask sessions
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # Configure session cookies

# Using the ORM operations of Flask-SQLAlchemy to utilize
# Flask extensions like Flask-Login
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
db.init_app(app)  # Attach the SQLAlchemy instance to the Flask app

# Using SQLAlchemy Core to run lower-level database operations
engine = create_engine(DATABASE_URL)  # Create an engine for SQLAlchemy Core

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

if FLASK_ENV == "development":
    print("Database URL: ", DATABASE_URL)


@login_manager.user_loader
def load_user(user_id):
    with db.session.begin():
        return db.session.get(Account, int(user_id))


# metadata.create_all(engine)  # Create the tables if they don't exist
populate_categories_table(engine, categories_table, CATEGORY_LIST)


@app.route('/')
def serve_vue_app():
    return send_from_directory(app.static_folder, 'index.html')

# ---------------------------------- Main GET APIs ----------------------------------

@app.route('/api/hello', methods=["GET"])
def hello_world():
    return jsonify(message='Hello from Flask!')

@app.route('/api/get_expenses', methods=["GET"])
@login_required_api
def get_expenses():

    # Create a conditional expression for PersonName
    person_name_expr = case(
        (expenses_table.c.PersonID == null(), "Joint"),
        else_=persons_table.c.PersonName
    ).label("PersonName")

    # Create a SQL query to select expenses and join with the persons table
    query = select(
        expenses_table.c.ExpenseDate,
        expenses_table.c.Amount,
        expenses_table.c.ExpenseCategory,
        expenses_table.c.AdditionalNotes,
        expenses_table.c.Currency,
        person_name_expr
    ).select_from(
        expenses_table.join(persons_table, expenses_table.c.PersonID == persons_table.c.PersonID, isouter=True)
    ).where(expenses_table.c.AccountID == current_user.id)

    # Execute the query using SQLAlchemy Core
    with engine.connect() as connection:
        result = connection.execute(query)
        user_expenses = result.fetchall()

    # Convert raw results to a list of dicts
    expenses = [row._asdict() for row in user_expenses]

    # Format the amount in each expense
    for expense in expenses:
        if expense["Currency"] == "USD":
            expense["Amount"] = "${:,.2f}".format(expense["Amount"])
        elif expense["Currency"] == "EUR":
            expense["Amount"] = "€{:,.2f}".format(expense["Amount"])

    return jsonify({"success": True, "expenses": expenses})


# ------------------------------- Auxilliary GET APIs -------------------------------

@app.route('/api/get_categories', methods=["GET"])
@login_required_api
def get_categories_api():
    # Fetch and return all the (default) expense categories
    categories = get_categories(engine, categories_table)
    return jsonify({"categories": categories})


@app.route('/api/get_persons', methods=["GET"])
@login_required_api
def get_persons_api():
    # Fetch and return persons associated with the current user's account
    persons = Person.query.filter_by(AccountID=current_user.id).all()
    persons_json = [person.to_json() for person in persons]
    return jsonify(persons_json)


# ---------------------------------- POST APIs ----------------------------------

@app.route('/api/submit_expenses', methods=['POST'])
@login_required_api
def submit_new_expenses():

    try:
        # Parse JSON data from request
        data = request.json
        expenses = data['expenses']
        counter = 0

        try:
            with engine.connect() as conn:
                for expense in expenses:
                    try:
                        # Extract individual fields from the expense dictionary
                        scope = expense['scope']
                        day = expense['day']
                        month = expense['month']
                        year = expense['year']
                        amount = expense['amount']
                        category = expense['category']
                        notes = expense['notes']

                        expense_date = datetime.strptime(
                            f"{year}-{month}-{day}", "%Y-%B-%d"
                        ).date()

                        # Determine if the scope is joint or individual
                        person_id = None if scope == "Joint" else scope
                        expense_scope = "Joint" if scope == "Joint" else "Individual"

                        # TODO: Validate that any person_id is associated with the current user's account

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
                    
                    except ValueError as e:
                        # Handle invalid date
                        print("Invalid date:", day, month, year)
                        continue  # TODO: Handle this invalid date. For now, skip it.
                
                # Commit all the changes to the database
                conn.commit()

                return jsonify({"success": True, "message": f"{counter} expenses successfully recorded."})
            
        except SQLAlchemyError as e:
            if FLASK_ENV == "development":
                print(e)
            return jsonify({"success": False, "error": "Database error"})

    except BadRequestKeyError:
        return jsonify({"success": False, "error": "Invalid request"})

# --------------------------------- Security APIs ------------------------------

@app.route("/api/login", methods=["POST"])
def login():
    try:
        # Parse JSON data from request
        data = request.get_json()
        username_or_email = data.get("username")
        password = data.get("password")

        user = Account.query.filter(
            (Account.account_name == username_or_email) | 
            (Account.user_email == username_or_email)
        ).first()

        if user and user.check_password(password):
            login_and_update_last_login(user, engine)
            return jsonify(
            {
                'authenticated': True,
                'username': current_user.account_name,
                'display_name': current_user.display_name
            })
        else:
            return jsonify({"authenticated": False, "error": "Invalid username/email or password"}), 401
    except BadRequestKeyError:
        return jsonify({"authenticated": False, "error": "Invalid request"}), 400
    

@app.route("/api/create_account", methods=["POST"])
def create_account():
    try:
        # Parse JSON data from request
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        # Check if username already exists
        existing_user_by_username = Account.query.filter_by(
            account_name=username
        ).first()
        if existing_user_by_username:
            return jsonify({"success": False, "error": "Username already exists."})
        else:
            # Check if email already exists
            existing_user_by_email = Account.query.filter_by(user_email=email).first()
            if existing_user_by_email:
                return jsonify({"success": False, "error": "Email address already exists."}) 
            else:
                # Create new user instance
                new_user = Account(
                    account_name=username,
                    user_email=email,
                    display_name=username, # Default to display name = username
                    currency="USD",  # Default to USD
                )

                # Set password (this will hash the password)
                new_user.set_password(password)

                # Add new user to database
                db.session.add(new_user)
                db.session.commit()

                # Create a new Person instance associated with this account
                new_person = Person(AccountID=new_user.id, PersonName=username)

                # Add new person to database
                db.session.add(new_person)
                db.session.commit()

                # Authenticate and login the new user
                login_and_update_last_login(new_user, engine)

                return jsonify(
                {
                    'success': True,
                    'authenticated': True,
                    'username': current_user.account_name,
                    'display_name': current_user.display_name
                })

    except BadRequestKeyError:
        return jsonify({"success": False, "error": "Invalid request"})


@app.route("/api/logout")
def logout():
    logout_user()
    return jsonify({'success': True})


@app.route('/api/auth/status')
def auth_status():

    if current_user.is_authenticated:
        return jsonify(
            {
                'authenticated': True,
                'username': current_user.account_name,
                'display_name': current_user.display_name
            })
    else:
        return jsonify({'authenticated': False})


# -------------------------------- Main Execution ------------------------------

if __name__ == "__main__":
    if FLASK_ENV == "development":
        app.run(debug=True, port=5000)
    else:
        app.run(debug=False)