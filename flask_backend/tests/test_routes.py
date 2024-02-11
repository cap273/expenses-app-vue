import pytest
from dotenv import load_dotenv, find_dotenv
from flask import json
from flask_backend.create_app import create_app
from flask_backend.database.models import db


# Load test environment variables before setting up the application context
@pytest.fixture(scope='session', autouse=True)
def load_test_env():
    dotenv_path = find_dotenv('.env.test', usecwd=True)
    load_dotenv(dotenv_path=dotenv_path, override=True)

# Application fixture
@pytest.fixture
def app():
    _app = create_app()
    _app.testing = True
    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()

# Client fixture for making requests to the app
@pytest.fixture
def client(app):
    return app.test_client()

# Initialize and tear down the database for each test
@pytest.fixture
def init_database():
    db.create_all() # Setup phase
    yield db # Yield control back to the test function
    db.drop_all() # Teardown phase

# Example test case using the client and init_database fixtures
def test_create_persons(client, init_database):
    # Assuming you have a login route to authenticate and set up a session
    # You would need to authenticate here to test the route properly

    # Example person data
    persons_data = {
        "persons": [
            {"person_name": "John Doe"},
            {"person_name": "Jane Doe"}
        ]
    }

    response = client.post("/api/create_persons", data=json.dumps(persons_data), content_type='application/json')
    data = json.loads(response.data)

    assert response.status_code == 200
    assert data["success"] is True
    assert "2 person(s) successfully added." in data["message"]
