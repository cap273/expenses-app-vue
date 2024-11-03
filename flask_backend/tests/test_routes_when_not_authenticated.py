import pytest
from flask import json


def test_auth_status(client, init_database):
    response = client.get("/api/auth/status")
    auth_status = response.get_json()

    assert response.status_code == 200
    assert auth_status["authenticated"] is False


def test_invalid_login(client, init_database):
    response = client.post(
        "/api/login",
        data=json.dumps({"username": "invaliduser", "password": "invalidpassword"}),
        content_type="application/json",
    )
    login_status = response.get_json()

    assert response.status_code == 401
    assert login_status["authenticated"] is False
    assert login_status["error"] == "Invalid username/email or password"

    response = client.get("/api/auth/status")
    auth_status = response.get_json()

    assert response.status_code == 200
    assert auth_status["authenticated"] is False


def test_unauthenticated_get_routes(client, init_database):
    # Test all GET routes that require authentication
    routes = [
        "/api/get_persons",
        "/api/get_expenses",
        "/api/get_categories",
        "/api/get_scopes",  # New route
        "/api/get_pending_invites",  # New route
        "/api/get_household_members?scopeId=1"  # New route
    ]

    for route in routes:
        response = client.get(route)
        response_data = response.get_json()

        assert response.status_code == 401, f"Route {route} should return 401"
        assert isinstance(response_data, dict), f"Response for {route} is not a JSON object"
        assert list(response_data.keys()) == ["error"], f"JSON object for {route} contains keys other than 'error'"
        assert response_data["error"] == "Unauthorized"


def test_unauthenticated_post_routes(client, init_database):
    # Test all POST routes that require authentication
    routes_and_data = [
        ("/api/create_persons", {"persons": [{"person_name": "Test"}]}),
        ("/api/submit_expenses", {"expenses": [{"amount": 100}]}),
        ("/api/delete_expenses", {"expenseIds": [1]}),
        ("/api/create_household", {"name": "Test House"}),  # New route
        ("/api/invite_to_household", {"email": "test@test.com", "scopeId": 1}),  # New route
        ("/api/respond_to_invite", {"scopeId": 1, "response": "accept"}),  # New route
        ("/api/leave_household", {"scopeId": 1}),  # New route
        ("/api/delete_household", {"scopeId": 1}),  # New route
        ("/api/remove_household_member", {"scopeId": 1, "email": "test@test.com"})  # New route
    ]

    for route, data in routes_and_data:
        response = client.post(
            route,
            data=json.dumps(data),
            content_type="application/json"
        )
        response_data = response.get_json()

        assert response.status_code == 401, f"Route {route} should return 401"
        assert isinstance(response_data, dict), f"Response for {route} is not a JSON object"
        assert list(response_data.keys()) == ["error"], f"JSON object for {route} contains keys other than 'error'"
        assert response_data["error"] == "Unauthorized"