import pytest

from app import app
from config import db
from models import User, Expense


def register(client, username="testuser", password="password123"):
    return client.post(
        "/signup",
        json={
            "username": username,
            "password": password,
            "password_confirmation": password,
        },
    )


def login(client, username="testuser", password="password123"):
    response = client.post(
        "/login",
        json={"username": username, "password": password},
    )
    return response.json["token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_signup_creates_user_and_returns_token(client):
    response = register(client)

    assert response.status_code == 201
    assert response.json["user"]["username"] == "testuser"
    assert "token" in response.json

    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        assert user is not None
        assert user.authenticate("password123")

        # Passwords must be stored as hashes, not plain text.
        assert user._password_hash != "password123"

        # The password hash must not be publicly accessible.
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


def test_login_and_current_user(client):
    register(client)

    response = client.post(
        "/login",
        json={"username": "testuser", "password": "password123"},
    )

    assert response.status_code == 200
    token = response.json["token"]

    me_response = client.get("/me", headers=auth_headers(token))

    assert me_response.status_code == 200
    assert me_response.json["username"] == "testuser"


def test_login_rejects_wrong_password(client):
    register(client)

    response = client.post(
        "/login",
        json={"username": "testuser", "password": "wrongpassword"},
    )

    assert response.status_code == 401


def test_protected_routes_reject_unauthenticated_requests(client):
    assert client.get("/me").status_code == 401
    assert client.get("/expenses").status_code == 401
    assert client.post(
        "/expenses",
        json={"title": "Test expense", "amount": 100},
    ).status_code == 401
    assert client.patch(
        "/expenses/1",
        json={"amount": 200},
    ).status_code == 401
    assert client.delete("/expenses/1").status_code == 401
    assert client.delete("/logout").status_code == 401

def test_expense_crud_and_pagination(client):
    register(client)
    token = login(client)
    headers = auth_headers(token)

    for number in range(3):
        response = client.post(
            "/expenses",
            headers=headers,
            json={
                "title": f"Expense {number}",
                "amount": 100 + number,
                "category": "Food",
            },
        )
        assert response.status_code == 201

    list_response = client.get(
        "/expenses?page=1&per_page=2",
        headers=headers,
    )

    assert list_response.status_code == 200
    assert len(list_response.json["expenses"]) == 2
    assert list_response.json["total"] == 3
    assert list_response.json["pages"] == 2

    expense_id = list_response.json["expenses"][0]["id"]

    detail_response = client.get(
        f"/expenses/{expense_id}",
        headers=headers,
    )
    assert detail_response.status_code == 200

    update_response = client.patch(
        f"/expenses/{expense_id}",
        headers=headers,
        json={"amount": 999, "category": "Updated"},
    )
    assert update_response.status_code == 200
    assert update_response.json["amount"] == 999

    delete_response = client.delete(
        f"/expenses/{expense_id}",
        headers=headers,
    )
    assert delete_response.status_code == 204

    missing_response = client.get(
        f"/expenses/{expense_id}",
        headers=headers,
    )
    assert missing_response.status_code == 404


def test_users_cannot_access_another_users_expenses(client):
    register(client, username="alice")
    alice_token = login(client, username="alice")
    alice_headers = auth_headers(alice_token)

    create_response = client.post(
        "/expenses",
        headers=alice_headers,
        json={"title": "Alice expense", "amount": 500},
    )
    assert create_response.status_code == 201
    expense_id = create_response.json["id"]

    register(client, username="bob")
    bob_token = login(client, username="bob")
    bob_headers = auth_headers(bob_token)

    # Bob must not see Alice's expense in his list.
    list_response = client.get("/expenses", headers=bob_headers)
    assert list_response.status_code == 200
    assert list_response.json["total"] == 0

    # Bob must not read Alice's expense.
    get_response = client.get(
        f"/expenses/{expense_id}",
        headers=bob_headers,
    )
    assert get_response.status_code == 404

    # Bob must not update Alice's expense.
    update_response = client.patch(
        f"/expenses/{expense_id}",
        headers=bob_headers,
        json={"amount": 9999},
    )
    assert update_response.status_code == 404

    # Bob must not delete Alice's expense.
    delete_response = client.delete(
        f"/expenses/{expense_id}",
        headers=bob_headers,
    )
    assert delete_response.status_code == 404

    # Alice's original expense must remain unchanged.
    owner_response = client.get(
        f"/expenses/{expense_id}",
        headers=alice_headers,
    )
    assert owner_response.status_code == 200
    assert owner_response.json["amount"] == 500


def test_expense_validation_rejects_invalid_amount(client):
    register(client)
    token = login(client)

    response = client.post(
        "/expenses",
        headers=auth_headers(token),
        json={"title": "Invalid expense", "amount": -10},
    )

    assert response.status_code == 422


def test_logout_endpoint(client):
    register(client)
    token = login(client)

    response = client.delete(
        "/logout",
        headers=auth_headers(token),
    )

    assert response.status_code == 204

    # A revoked token must no longer access protected routes.
    me_response = client.get(
        "/me",
        headers=auth_headers(token),
    )

    assert me_response.status_code == 401
