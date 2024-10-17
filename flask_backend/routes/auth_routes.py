from flask import Blueprint, jsonify, request, current_app
from flask_login import (
    logout_user,
    current_user,
    login_required,
)
from werkzeug.exceptions import BadRequestKeyError
from werkzeug.security import generate_password_hash
import re  # Import for regular expressions

from flask_backend.utils.session import login_and_update_last_login
from flask_backend.database.models import db, Account

auth_routes = Blueprint("auth_routes", __name__)

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
            login_and_update_last_login(user, current_app.config["ENGINE"])
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

@auth_routes.route('/api/change_password', methods=['POST'])
@login_required
def change_password():
    try:
        # Parse JSON data from request
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')

        # Validate input
        if not current_password or not new_password:
            return jsonify({'success': False, 'error': 'Missing required fields.'}), 400

        # Get the current user from the database
        user = Account.query.get(current_user.id)

        # Check if current password is correct
        if not user.check_password(current_password):
            return jsonify({'success': False, 'error': 'Current password is incorrect.'}), 400

        # Optional: Add password strength validation for new_password
        if len(new_password) < 8:
            return jsonify({'success': False, 'error': 'New password must be at least 8 characters long.'}), 400

        # Update the user's password
        user.password = generate_password_hash(new_password)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Password changed successfully.'}), 200

    except Exception as e:
        # Optionally log the error
        # current_app.logger.error(f'Error changing password: {e}')
        return jsonify({'success': False, 'error': 'An error occurred while changing the password.'}), 500

@auth_routes.route('/api/update_profile', methods=['POST'])
@login_required
def update_profile():
    try:
        # Parse JSON data from request
        data = request.get_json()
        new_username = data.get('new_username')
        current_password = data.get('current_password')
        new_password = data.get('new_password')

        # Get the current user from the database
        user = Account.query.get(current_user.id)

        # Initialize a flag to track if the user data has changed
        data_changed = False

        # Handle Username Change
        if new_username:
            # Validate new username
            if not re.match(r'^[a-zA-Z0-9_]{3,20}$', new_username):
                return jsonify({'success': False, 'error': 'Invalid username.'}), 400

            # Check if username is already taken
            existing_user = Account.query.filter_by(account_name=new_username).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({'success': False, 'error': 'Username is already taken.'}), 400

            user.account_name = new_username
            data_changed = True

        # Handle Password Change
        if new_password:
            # Validate current password
            if not current_password or not user.check_password(current_password):
                return jsonify({'success': False, 'error': 'Current password is incorrect.'}), 400

            # Validate new password strength
            if len(new_password) < 8:
                return jsonify({'success': False, 'error': 'New password must be at least 8 characters long.'}), 400

            # Update password
            user.password = generate_password_hash(new_password)
            data_changed = True

        if data_changed:
            db.session.commit()
            response = {'success': True, 'message': 'Profile updated successfully.'}
            if new_username:
                response['updated_username'] = new_username
            return jsonify(response), 200
        else:
            return jsonify({'success': False, 'error': 'No changes detected.'}), 400

    except Exception as e:
        # Optionally log the error
        # current_app.logger.error(f'Error updating profile: {e}')
        return jsonify({'success': False, 'error': 'An error occurred while updating the profile.'}), 500
