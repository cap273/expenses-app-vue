import pytest
from dotenv import load_dotenv, find_dotenv
from flask_backend.create_app import create_app
from flask_backend.database.models import Account, db
from flask_backend.utils.db_tools import populate_categories_table
from flask_backend.database.tables import categories_table, CATEGORY_LIST
from werkzeug.security import generate_password_hash

# Add root of the project to sys.path
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


@pytest.fixture(scope="session", autouse=True)
def load_test_env():
    dotenv_path = find_dotenv(".env.test", usecwd=True)
    load_dotenv(dotenv_path=dotenv_path, override=True)


@pytest.fixture
def app():
    _app = create_app()
    _app.testing = True
    ctx = _app.app_context()
    ctx.push()
    yield _app
    ctx.pop()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def init_database(app):
    db.create_all()
    populate_categories_table(app.config["ENGINE"], categories_table, CATEGORY_LIST)
    yield db
    db.drop_all()


@pytest.fixture
def test_user(app, init_database):
    email = "user@example.com"
    username = "testuser"
    password = "testpass"
    hashed_password = generate_password_hash(password)
    user = Account(user_email=email, account_name=username, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return user
