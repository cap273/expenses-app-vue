import pytest
from flask import json


def test_create_account_success(client, init_database):
    """
    Test successful creation of a new account.
    """
    # Define a valid payload
    valid_payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "aSecurePassword",
    }

    # Make a POST request to the create_account endpoint
    response = client.post(
        "/api/create_account",
        data=json.dumps(valid_payload),
        content_type="application/json",
    )
    response_data = json.loads(response.data)

    # Assertions
    assert response.status_code == 200
    assert response_data["success"] is True
    assert response_data["authenticated"] is True
    assert response_data["username"] == "newuser"
    assert "display_name" in response_data


def test_create_account_failure_due_to_short_username(client, init_database):
    """
    Test account creation failure due to a short username.
    """
    # Define an invalid payload with a short username
    invalid_payload = {
        "username": "nu",
        "email": "user@example.com",
        "password": "aSecurePassword",
    }

    # Make a POST request to the create_account endpoint
    response = client.post(
        "/api/create_account",
        data=json.dumps(invalid_payload),
        content_type="application/json",
    )
    response_data = json.loads(response.data)

    # Assertions
    assert (
        response.status_code == 200
    )  # Adjust according to your actual response status code for validation errors
    assert response_data["success"] is False
    assert "error" in response_data
    assert "Username must be longer than 3 characters." in response_data["error"]


def test_create_account_failure_due_to_existing_username(client, init_database):
    """
    Test account creation failure due to an existing username.
    """
    # First, create an account
    client.post(
        "/api/create_account",
        data=json.dumps(
            {
                "username": "existinguser",
                "email": "existinguser@example.com",
                "password": "aSecurePassword",
            }
        ),
        content_type="application/json",
    )

    # Attempt to create another account with the same username
    duplicate_username_payload = {
        "username": "existinguser",
        "email": "newemail@example.com",
        "password": "anotherSecurePassword",
    }
    response = client.post(
        "/api/create_account",
        data=json.dumps(duplicate_username_payload),
        content_type="application/json",
    )
    response_data = json.loads(response.data)

    # Assertions
    assert (
        response.status_code == 200
    )  # Adjust according to your actual response status code for validation errors
    assert response_data["success"] is False
    assert "error" in response_data
    assert "Username already exists." in response_data["error"]
