import os
import logging
from dotenv import load_dotenv

from flask import Flask, send_from_directory
from sqlalchemy import create_engine, text
from flask_login import LoginManager

from flask_backend.utils.db_tools import (
    populate_categories_table,
    get_database_url,
)
from flask_backend.database.models import db, Account
from flask_backend.database.tables import (
    categories_table,
    CATEGORY_LIST,
    scopes_table,
    scope_access_table,
    expenses_table,  # Added this import
)

from flask_backend.routes.account_routes import account_routes
from flask_backend.routes.auth_routes import auth_routes
from flask_backend.routes.expense_routes import expense_routes
from flask_backend.routes.household_routes import household_routes


# Initialize Flask-Login
login_manager = LoginManager()

# Load environment variables from .env file
load_dotenv()


def create_app(test_config=None):
    app = Flask(__name__, static_folder="../vue-frontend/dist", static_url_path="/")

    if test_config is None:
        DATABASE_URL = get_database_url(
            os.getenv("DB_USERNAME"),
            os.getenv("DB_PASSWORD"),
            os.getenv("DB_SERVER"),
            os.getenv("DB_NAME"),
        )
        app.config["FLASK_ENV"] = os.getenv("FLASK_ENV")
    else:
        DATABASE_URL = get_database_url(
            test_config["DB_USERNAME"],
            test_config["DB_PASSWORD"],
            test_config["DB_SERVER"],
            test_config["DB_NAME"],
        )
        app.config["FLASK_ENV"] = test_config["FLASK_ENV"]

    # Configure logging based on the environment
    if app.config["FLASK_ENV"] == "development":
        logging.basicConfig()
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    # Using the ORM operations of Flask-SQLAlchemy to utilize
    # Flask extensions like Flask-Login
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL

    # Using SQLAlchemy Core to run lower-level database operations
    app.config["ENGINE"] = create_engine(DATABASE_URL)

    if app.config["FLASK_ENV"] == "development":
        print("Database URL: ", DATABASE_URL)

    # Set the secret key to use for Flask sessions
    app.secret_key = os.getenv("FLASK_SECRET_KEY")

    # Configure session cookies
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Attach the SQLAlchemy instance to the Flask app
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return Account.query.get(int(user_id))

    # Create tables in correct order
    with app.app_context():
        # Create/recreate other tables
        db.create_all()
        populate_categories_table(app.config["ENGINE"], categories_table, CATEGORY_LIST)
        scopes_table.create(app.config["ENGINE"], checkfirst=True)
        scope_access_table.create(app.config["ENGINE"], checkfirst=True)


    # Register blueprints
    app.register_blueprint(account_routes)
    app.register_blueprint(auth_routes)
    app.register_blueprint(expense_routes)
    app.register_blueprint(household_routes)

    @app.route("/")
    def serve_vue_app():
        return send_from_directory(app.static_folder, "index.html")

    return app