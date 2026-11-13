def test_account_isolation(client, create_account):

    account1 = create_account(
        username="lukas",
        name="Lukas",
        surname="Test"
    )

    user_response = client.post(
        "/users",
        json={
            "name": "Matas",
            "surname": "Test"
        }
    )

    assert user_response.status_code == 201
    member_id = user_response.json()["id"]

    group_response = client.post(
        "/groups",
        json={
            "name": "Privati grupė",
            "member_ids": [member_id]
        }
    )

    assert group_response.status_code == 201
    group_id = group_response.json()["id"]

    own_response = client.get(
        f"/groups/{group_id}/balances"
    )

    assert own_response.status_code == 200
    assert own_response.json()["group_name"] == "Privati grupė"

    logout_response = client.post("/auth/logout")
    assert logout_response.status_code == 200

    account2 = create_account(
        username="tomas",
        name="Tomas",
        surname="Test"
    )

    assert account1["id"] != account2["id"]

    groups_response = client.get("/groups")

    assert groups_response.status_code == 200
    assert groups_response.json() == []

    wrong_response = client.get(
        f"/groups/{group_id}/balances"
    )

    assert wrong_response.status_code == 404
    assert wrong_response.json()["detail"] == "Grupė nerasta"

    expense_response = client.post(
        f"/groups/{group_id}/expenses",
        json={
            "paid_by": account2["user_id"],
            "amount": "50.00"
        }
    )

    assert expense_response.status_code == 404

    delete_response = client.delete(
        f"/groups/{group_id}/expenses"
    )

    assert delete_response.status_code == 404
