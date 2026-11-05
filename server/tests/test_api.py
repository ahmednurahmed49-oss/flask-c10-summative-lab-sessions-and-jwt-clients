def register(client, username="testuser", password="password123"):
    return client.post(
        "/signup",
        json={
            "username": username,
            "password": password,
            "password_confirmation": password,
        },
    )


def test_expense_routes_reject_unauthenticated_requests(client):
    assert client.get("/expenses").status_code == 401

    assert client.post(
        "/expenses",
        json={"title": "Test expense", "amount": 100},
    ).status_code == 401

    assert client.get("/expenses/1").status_code == 401

    assert client.patch(
        "/expenses/1",
        json={"amount": 200},
    ).status_code == 401

    assert client.delete("/expenses/1").status_code == 401


def test_expense_crud_and_pagination(client):
    register(client)

    for number in range(3):
        response = client.post(
            "/expenses",
            json={
                "title": f"Expense {number}",
                "amount": 100 + number,
                "category": "Food",
            },
        )
        assert response.status_code == 201

    list_response = client.get("/expenses?page=1&per_page=2")

    assert list_response.status_code == 200
    assert len(list_response.json["expenses"]) == 2
    assert list_response.json["total"] == 3
    assert list_response.json["pages"] == 2

    expense_id = list_response.json["expenses"][0]["id"]

    detail_response = client.get(f"/expenses/{expense_id}")
    assert detail_response.status_code == 200

    update_response = client.patch(
        f"/expenses/{expense_id}",
        json={"amount": 999, "category": "Updated"},
    )
    assert update_response.status_code == 200
    assert update_response.json["amount"] == 999

    delete_response = client.delete(f"/expenses/{expense_id}")
    assert delete_response.status_code == 204

    missing_response = client.get(f"/expenses/{expense_id}")
    assert missing_response.status_code == 404


def test_users_cannot_access_another_users_expenses(client):
    register(client, username="alice")

    create_response = client.post(
        "/expenses",
        json={"title": "Alice expense", "amount": 500},
    )
    assert create_response.status_code == 201
    expense_id = create_response.json["id"]

    client.delete("/logout")
    register(client, username="bob")

    list_response = client.get("/expenses")
    assert list_response.status_code == 200
    assert list_response.json["total"] == 0

    assert client.get(f"/expenses/{expense_id}").status_code == 404

    assert client.patch(
        f"/expenses/{expense_id}",
        json={"amount": 9999},
    ).status_code == 404

    assert client.delete(f"/expenses/{expense_id}").status_code == 404

    client.delete("/logout")

    login_response = client.post(
        "/login",
        json={"username": "alice", "password": "password123"},
    )
    assert login_response.status_code == 200

    owner_response = client.get(f"/expenses/{expense_id}")
    assert owner_response.status_code == 200
    assert owner_response.json["amount"] == 500


def test_expense_validation_rejects_invalid_amount(client):
    register(client)

    response = client.post(
        "/expenses",
        json={"title": "Invalid expense", "amount": -10},
    )

    assert response.status_code == 422


def test_expense_validation_rejects_invalid_date(client):
    register(client)

    response = client.post(
        "/expenses",
        json={
            "title": "Invalid date",
            "amount": 100,
            "date": "not-a-date",
        },
    )

    assert response.status_code == 422
