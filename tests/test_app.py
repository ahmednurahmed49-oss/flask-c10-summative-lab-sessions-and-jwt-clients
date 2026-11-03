from config import db
from models import User


def test_signup_creates_user(client):
    res = client.post("/signup", json={"username": "ann", "password": "pw12345"})
    assert res.status_code == 201
    assert res.get_json()["username"] == "ann"


def test_signup_duplicate_username(client):
    client.post("/signup", json={"username": "ann", "password": "pw12345"})
    res = client.post("/signup", json={"username": "ann", "password": "other"})
    assert res.status_code == 422


def test_signup_missing_fields(client):
    assert client.post("/signup", json={"username": "ann"}).status_code == 422


def test_password_is_hashed(logged_in):
    user = User.query.filter_by(username="peter").first()
    assert user._password_hash != "TONKATONKA"


def test_login_success_and_failure(client):
    client.post("/signup", json={"username": "ann", "password": "pw12345"})
    assert client.post("/login", json={"username": "ann", "password": "pw12345"}).status_code == 200
    assert client.post("/login", json={"username": "ann", "password": "wrong"}).status_code == 401


def test_check_session(client, logged_in):
    assert logged_in.get("/check_session").status_code == 200
    logged_in.delete("/logout")
    assert logged_in.get("/check_session").status_code == 401


def test_logout_returns_204(logged_in):
    assert logged_in.delete("/logout").status_code == 204


def test_expenses_require_login(client):
    assert client.get("/expenses").status_code == 401
    assert client.post("/expenses", json={"title": "x", "amount": 1}).status_code == 401


def test_create_expense(logged_in):
    res = logged_in.post("/expenses", json={"title": "Lunch", "amount": 12.5, "category": "Food"})
    assert res.status_code == 201
    assert res.get_json()["title"] == "Lunch"


def test_create_expense_invalid(logged_in):
    assert logged_in.post("/expenses", json={"title": "", "amount": 5}).status_code == 422
    assert logged_in.post("/expenses", json={"title": "Bad", "amount": -5}).status_code == 422


def test_update_expense(logged_in):
    exp = logged_in.post("/expenses", json={"title": "Taxi", "amount": 20}).get_json()
    res = logged_in.patch(f"/expenses/{exp['id']}", json={"amount": 25})
    assert res.status_code == 200
    assert res.get_json()["amount"] == 25


def test_delete_expense(logged_in):
    exp = logged_in.post("/expenses", json={"title": "Taxi", "amount": 20}).get_json()
    assert logged_in.delete(f"/expenses/{exp['id']}").status_code == 204
    assert logged_in.patch(f"/expenses/{exp['id']}", json={"amount": 1}).status_code == 404


# ---------- Pagination ----------
def test_pagination(logged_in):
    for i in range(7):
        logged_in.post("/expenses", json={"title": f"Item {i}", "amount": i + 1})
    page1 = logged_in.get("/expenses?page=1&per_page=5").get_json()
    page2 = logged_in.get("/expenses?page=2&per_page=5").get_json()
    assert len(page1["expenses"]) == 5
    assert len(page2["expenses"]) == 2
    assert page1["total"] == 7 and page1["pages"] == 2


# ---------- Users can only see their own data ----------
def test_cannot_touch_other_users_expense(client):
    client.post("/signup", json={"username": "ann", "password": "pw12345"})
    exp = client.post("/expenses", json={"title": "Ann's", "amount": 10}).get_json()
    client.delete("/logout")

    client.post("/signup", json={"username": "bob", "password": "pw12345"})
    assert client.get("/expenses").get_json()["total"] == 0
    assert client.patch(f"/expenses/{exp['id']}", json={"amount": 1}).status_code == 404
    assert client.delete(f"/expenses/{exp['id']}").status_code == 404