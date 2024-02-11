from flask import Blueprint, jsonify, request, current_app
from flask_login import (
    logout_user,
    current_user,
)
from werkzeug.exceptions import BadRequestKeyError

from flask_backend.utils.session import login_and_update_last_login
from flask_backend.database.models import db, Account


auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route("/api/login", methods=["POST"])
def login():
    try:
        # Parse JSON data from request
        data = request.get_json()
        username_or_email = data.get("username")
        password = data.get("password")

        user = Account.query.filter(
            (Account.account_name == username_or_email)
            | (Account.user_email == username_or_email)
        ).first()

        if user and user.check_password(password):
            login_and_update_last_login(user, current_app.config['ENGINE'])
            return jsonify(
                {
                    "authenticated": True,
                    "username": current_user.account_name,
                    "display_name": current_user.display_name,
                }
            )
        else:
            return (
                jsonify(
                    {
                        "authenticated": False,
                        "error": "Invalid username/email or password",
                    }
                ),
                401,
            )
    except BadRequestKeyError:
        return jsonify({"authenticated": False, "error": "Invalid request"}), 400


@auth_routes.route("/api/logout")
def logout():
    logout_user()
    return jsonify({"success": True})


@auth_routes.route("/api/auth/status")
def auth_status():
    if current_user.is_authenticated:
        return jsonify(
            {
                "authenticated": True,
                "username": current_user.account_name,
                "display_name": current_user.display_name,
            }
        )
    else:
        return jsonify({"authenticated": False})
    