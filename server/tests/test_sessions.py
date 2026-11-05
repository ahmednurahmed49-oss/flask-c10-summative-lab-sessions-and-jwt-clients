import pytest

from app import app
from models import User


def register(client, username="testuser", password="password123"):
    return client.post(
        "/signup",
        json={
            "username": username,
            "password": password,
            "password_confirmation": password,
        },
    )


def test_session_signup(client):
    response = register(client, username="sessionuser")

    assert response.status_code == 201
    assert response.json["username"] == "sessionuser"
    assert "token" not in response.json
    assert "user" not in response.json

    session_response = client.get("/check_session")

    assert session_response.status_code == 200
    assert session_response.json["username"] == "sessionuser"


def test_signup_stores_hashed_password(client):
    response = register(client)

    assert response.status_code == 201

    with app.app_context():
        user = User.query.filter_by(username="testuser").first()

        assert user is not None
        assert user.authenticate("password123")
        assert user._password_hash != "password123"

        with pytest.raises(AttributeError):
            _ = user.password_hash


def test_signup_rejects_duplicate_username(client):
    register(client)

    response = register(client)

    assert response.status_code == 409


def test_signup_rejects_short_password(client):
    response = register(client, password="short")

    assert response.status_code == 422


def test_signup_rejects_password_mismatch(client):
    response = client.post(
        "/signup",
        json={
            "username": "testuser",
            "password": "password123",
            "password_confirmation": "different123",
        },
    )

    assert response.status_code == 422


def test_session_login(client):
    register(client, username="loginuser")
    client.delete("/logout")

    response = client.post(
        "/login",
        json={
            "username": "loginuser",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    assert response.json["username"] == "loginuser"

    session_response = client.get("/check_session")

    assert session_response.status_code == 200
    assert session_response.json["id"] == response.json["id"]


def test_check_session_without_login(client):
    response = client.get("/check_session")

    assert response.status_code == 200
    assert response.json == {}


def test_session_logout(client):
    register(client, username="logoutuser")

    logout_response = client.delete("/logout")

    assert logout_response.status_code == 204
    assert client.get("/check_session").json == {}


def test_session_login_rejects_wrong_password(client):
    register(client, username="wrongpassworduser")
    client.delete("/logout")

    response = client.post(
        "/login",
        json={
            "username": "wrongpassworduser",
            "password": "incorrect123",
        },
    )

    assert response.status_code == 401
    assert client.get("/check_session").json == {}
