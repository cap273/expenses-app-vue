import pytest
from flask import json


# Test the login functionality
def test_login(client, test_user):
    # Define a valid payload
    valid_payload = {
        "username": test_user.account_name,
        "password": "testpass",
    }

    # Make a POST request to the login endpoint
    response = client.post(
        "/api/login", data=json.dumps(valid_payload), content_type="application/json"
    )
    assert response.status_code == 200
    assert response.json["authenticated"] is True


# Test the login with incorrect credentials
def test_login_failure(client, test_user):
    invalid_payload = {
        "username": test_user.account_name,
        "password": "wrongpassword",
    }

    response = client.post(
        "/api/login", data=json.dumps(invalid_payload), content_type="application/json"
    )
    assert response.status_code == 401
    assert response.json["authenticated"] is False


# Test the logout functionality
def test_logout(client, test_user, app):
    # First, log the user in
    client.post(
        "/api/login",
        data=json.dumps({"username": "testuser", "password": "testpass"}),
        content_type="application/json",
    )

    # Then, log the user out
    response = client.get("/api/logout")
    assert response.status_code == 200
    assert response.json["success"] is True


# Test the auth status endpoint
def test_auth_status(client, test_user, app):
    # Test unauthenticated status
    response = client.get("/api/auth/status")
    assert response.status_code == 200
    assert response.json["authenticated"] is False

    # Log in
    client.post(
        "/api/login",
        data=json.dumps({"username": "testuser", "password": "testpass"}),
        content_type="application/json",
    )

    # Test authenticated status
    response = client.get("/api/auth/status")
    assert response.status_code == 200
    assert response.json["authenticated"] is True
