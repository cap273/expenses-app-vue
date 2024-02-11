import pytest
from flask import json
from datetime import datetime
from flask_backend.database.models import db, Account, Person, Expense


@pytest.fixture
def setup_expenses(test_user, app):
    person = Person.query.filter_by(AccountID=test_user.id).first()
    if not person:
        person = Person(AccountID=test_user.id, PersonName=test_user.account_name)
        db.session.add(person)
        db.session.commit()

    # Add two expenses: an Individual and a Joint expense.
    expenses = [
        Expense(
            AccountID=test_user.id,
            ExpenseScope="Joint",
            Day=15,
            Month="January",
            Year=2021,
            ExpenseDate=datetime(2021, 1, 15),
            Amount=100.00,
            ExpenseCategory="Groceries",
            Currency="USD",
        ),
        Expense(
            AccountID=test_user.id,
            ExpenseScope="Individual",
            PersonID=person.PersonID,
            Day=16,
            Month="January",
            Year=2021,
            ExpenseDate=datetime(2021, 1, 16),
            Amount=50.00,
            ExpenseCategory="Entertainment",
            Currency="USD",
        ),
    ]
    db.session.add_all(expenses)
    db.session.commit()


def login_as_test_user(client):
    return client.post(
        "/api/login",
        data=json.dumps({"username": "testuser", "password": "testpass"}),
        content_type="application/json",
    )


def test_get_expenses(client, test_user, setup_expenses):
    login_as_test_user(client)
    response = client.get("/api/get_expenses")
    data = response.get_json()

    assert response.status_code == 200
    assert "success" in data
    assert data["success"] is True
    assert len(data["expenses"]) == 2


def test_get_categories(client, test_user):
    login_as_test_user(client)
    response = client.get("/api/get_categories")
    data = response.get_json()

    assert response.status_code == 200
    assert "categories" in data
    # Add more assertions based on the expected categories data


def test_submit_expenses(client, test_user, setup_expenses):
    login_as_test_user(client)
    new_expense = {
        "expenses": [
            {
                "scope": "Joint",
                "day": 20,
                "month": "February",
                "year": 2021,
                "amount": "200.00",
                "category": "Utilities",
                "notes": "Electric bill",
            }
        ]
    }
    response = client.post(
        "/api/submit_expenses",
        data=json.dumps(new_expense),
        content_type="application/json",
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True

    # Query the database to confirm the expense was added
    expense = Expense.query.filter_by(
        AccountID=test_user.id, ExpenseCategory="Utilities"
    ).first()
    assert expense is not None
    assert expense.Amount == 200.00
