from app import app
from config import db
from models import User


def test_session_signup(client):
    response = client.post(
        "/signup",
        json={
            "username": "sessionuser",
            "password": "password123",
            "password_confirmation": "password123",
        },
    )

    assert response.status_code == 201
    assert response.json["username"] == "sessionuser"
    assert response.json["user"]["username"] == "sessionuser"
    assert "token" in response.json

    session_response = client.get("/check_session")

    assert session_response.status_code == 200
    assert session_response.json["username"] == "sessionuser"


def test_session_login(client):
    client.post(
        "/signup",
        json={
            "username": "loginuser",
            "password": "password123",
            "password_confirmation": "password123",
        },
    )

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
    client.post(
        "/signup",
        json={
            "username": "logoutuser",
            "password": "password123",
            "password_confirmation": "password123",
        },
    )

    logout_response = client.delete("/logout")

    assert logout_response.status_code == 204

    session_response = client.get("/check_session")

    assert session_response.status_code == 200
    assert session_response.json == {}


def test_session_login_rejects_wrong_password(client):
    client.post(
        "/signup",
        json={
            "username": "wrongpassworduser",
            "password": "password123",
            "password_confirmation": "password123",
        },
    )

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
