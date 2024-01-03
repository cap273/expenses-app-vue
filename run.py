from flask import Flask, request, render_template, redirect, url_for, jsonify, send_from_directory
from sqlalchemy import create_engine, select, update
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
from flask_backend.utils.session import login_and_update_last_login
from flask_backend.database.models import db, Account, Person
from flask_backend.database.tables import (
    expenses_table,
    categories_table,
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

# ------------------ API Routes to serve JSON data ------------------------------

@app.route('/api/hello')
def hello_world():
    return jsonify(message='Hello from Flask!')

@app.route("/api/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


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

        print(user)
        if user and user.check_password(password):
            login_and_update_last_login(user, engine)
            return jsonify({"success": True, "username": user.account_name})
        else:
            return jsonify({"success": False, "error": "Invalid username/email or password"}), 401
    except BadRequestKeyError:
        return jsonify({"success": False, "error": "Invalid request"}), 400


# @app.route("/api/user_info")
# @login_required
# def user_info():
#     return jsonify(username=current_user.username)


# -------------------------------- Main Execution ------------------------------

if __name__ == "__main__":
    if FLASK_ENV == "development":
        app.run(debug=True, port=5000)
    else:
        app.run(debug=False)