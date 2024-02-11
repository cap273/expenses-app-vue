from functools import wraps
from flask import jsonify
from flask_login import login_user, current_user
from sqlalchemy import update, exc
from datetime import datetime, timezone

from ..database.models import Account


def login_and_update_last_login(user, engine):
    try:
        # Log in the user
        login_user(user)

        # Update the last login date using SQLAlchemy Core
        with engine.begin() as connection:  # Automatically begins a transaction
            stmt = (
                update(Account)
                .where(Account.id == user.id)
                .values(last_login_date=datetime.now(timezone.utc))
            )
            connection.execute(stmt)

        return True
    except exc.SQLAlchemyError as e:
        print("Error occurred during login or update:", e)
        return False


def login_required_api(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            # Return a 401 Unauthorized response
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)

    return decorated_function
