from flask import Blueprint, jsonify, request, current_app
from sqlalchemy.exc import SQLAlchemyError
import re
from dotenv import load_dotenv
from datetime import datetime
from flask_login import current_user
from werkzeug.exceptions import BadRequestKeyError

from flask_backend.utils.session import login_and_update_last_login, login_required_api
from flask_backend.database.models import db, Account, Person

account_routes = Blueprint("account_routes", __name__)


@account_routes.route("/api/create_account", methods=["POST"])
def create_account():
    try:
        # Parse JSON data from request
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        # Validate username length
        if len(username) <= 3:
            return jsonify(
                {
                    "success": False,
                    "error": "Username must be longer than 3 characters.",
                }
            )

        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"success": False, "error": "Invalid email address format."})

        # Validate password length
        if len(password) < 8:
            return jsonify(
                {"success": False, "error": "Password must be 8 characters or longer."}
            )

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
                return jsonify(
                    {"success": False, "error": "Email address already exists."}
                )
            else:
                # Create new user instance
                new_user = Account(
                    account_name=username,
                    user_email=email,
                    display_name=username,  # Default to display name = username
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
                login_and_update_last_login(new_user, current_app.config["ENGINE"])

                return jsonify(
                    {
                        "success": True,
                        "authenticated": True,
                        "username": current_user.account_name,
                        "display_name": current_user.display_name,
                    }
                )

    except BadRequestKeyError:
        return jsonify({"success": False, "error": "Invalid request"})


@account_routes.route("/api/get_persons", methods=["GET"])
@login_required_api
def get_persons_api():
    # Fetch and return persons associated with the current user's account
    persons = Person.query.filter_by(AccountID=current_user.id).all()
    persons_json = [person.to_json() for person in persons]
    return jsonify(persons_json)


@account_routes.route("/api/create_persons", methods=["POST"])
@login_required_api
def create_persons():
    try:
        data = request.json
        persons = data["persons"]
        successful_creations = 0

        if not persons:
            return jsonify({"success": False, "error": "No person data provided"})

        for person in persons:
            person_name = person.get("person_name")
            if not person_name:
                return jsonify(
                    {"success": False, "error": "Missing required field: person_name"}
                )

            new_person = Person(
                AccountID=current_user.id,
                PersonName=person_name,
                CreateDate=datetime.now(),
                LastUpdated=datetime.now(),
            )

            try:
                db.session.add(new_person)
                db.session.commit()
                successful_creations += 1
            except SQLAlchemyError as e:
                db.session.rollback()
                return jsonify({"success": False, "error": str(e)})

        return jsonify(
            {
                "success": True,
                "message": f"{successful_creations} person(s) successfully added.",
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
