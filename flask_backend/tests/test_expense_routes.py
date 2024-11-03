import pytest
from flask import json
from datetime import datetime
from flask_backend.database.models import db, Person, Expense


@pytest.fixture
def setup_expenses(test_user, test_scope, app):
    person = Person.query.filter_by(AccountID=test_user.id).first()
    if not person:
        person = Person(AccountID=test_user.id, PersonName=test_user.account_name)
        db.session.add(person)
        db.session.commit()

    # Add two expenses: a Joint expense and a Personal expense
    expenses = [
        Expense(
            ScopeID=test_scope.ScopeID,  # Using scope instead of account
            PersonID=None,  # Joint expense (no specific person)
            Day=15,
            Month="January",
            Year=2021,
            ExpenseDate=datetime(2021, 1, 15),
            Amount=100.00,
            ExpenseCategory="Groceries",
            Currency="USD",
        ),
        Expense(
            ScopeID=test_scope.ScopeID,  # Using scope instead of account
            PersonID=person.PersonID,  # Personal expense (linked to person)
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


def test_get_expenses(client, test_user, test_scope, login_as_test_user, setup_expenses):
    login_as_test_user()
    response = client.get("/api/get_expenses")
    data = response.get_json()

    assert response.status_code == 200
    assert "success" in data
    assert data["success"] is True
    assert len(data["expenses"]) == 2
    
    # Verify scope information is present
    for expense in data["expenses"]:
        assert "ScopeID" in expense
        assert expense["ScopeID"] == test_scope.ScopeID
        assert "ScopeName" in expense
        assert "ScopeType" in expense
        assert expense["ScopeType"] == "personal"


def test_get_categories(client, test_user, login_as_test_user):
    login_as_test_user()
    response = client.get("/api/get_categories")
    data = response.get_json()

    assert response.status_code == 200
    assert "categories" in data


def test_submit_expenses(client, test_user, test_scope, login_as_test_user):
    login_as_test_user()
    new_expense = {
        "expenses": [
            {
                "scope": test_scope.ScopeID,  # Using scope ID instead of account
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
        ScopeID=test_scope.ScopeID,  # Query by scope instead of account
        ExpenseCategory="Utilities"
    ).first()
    assert expense is not None
    assert expense.Amount == 200.00


def test_submit_expense_to_invalid_scope(client, test_user, test_scope, login_as_test_user):
    login_as_test_user()
    new_expense = {
        "expenses": [
            {
                "scope": 999999,  # Invalid scope ID
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
    assert data["success"] is False
    assert "error" in data


def test_delete_expenses(client, test_user, test_scope, login_as_test_user, setup_expenses):
    login_as_test_user()
    
    # First get the expenses to get their IDs
    response = client.get("/api/get_expenses")
    expenses = response.get_json()["expenses"]
    expense_ids = [expense["ExpenseID"] for expense in expenses]

    # Delete the expenses
    response = client.post(
        "/api/delete_expenses",
        data=json.dumps({"expenseIds": expense_ids}),
        content_type="application/json",
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True

    # Verify expenses were deleted
    remaining_expenses = Expense.query.filter_by(ScopeID=test_scope.ScopeID).all()
    assert len(remaining_expenses) == 0


def test_delete_expenses_from_unauthorized_scope(client, test_user, login_as_test_user):
    login_as_test_user()
    
    response = client.post(
        "/api/delete_expenses",
        data=json.dumps({"expenseIds": [999999]}),  # ID from unauthorized scope
        content_type="application/json",
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is False
    assert "message" in data
    assert "No expenses were deleted" in data["message"]