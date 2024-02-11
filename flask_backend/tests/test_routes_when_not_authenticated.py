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

    response = client.get("/api/get_persons")
    get_persons_response = response.get_json()

    assert response.status_code == 401
    assert isinstance(get_persons_response, dict), "Response is not a JSON object"
    assert list(get_persons_response.keys()) == [
        "error"
    ], "JSON object contains keys other than 'error'"
    assert get_persons_response["error"] == "Unauthorized"
