from decimal import Decimal


def test_invalid_expense(client):
    tenant = client.post(
        "/tenants",
        json={"name": "Test Tenant"}
    )
    assert tenant.status_code == 200
    tenant_id = tenant.json()["id"]

    user_ids = []

    for name in ["Lukas", "Tomas", "Matas"]:
        response = client.post(
            f"/tenants/{tenant_id}/users",
            json={"name": name, "surname": "Test"}
        )
        assert response.status_code == 200
        user_ids.append(response.json()["id"])

    group = client.post(
        f"/tenants/{tenant_id}/groups",
        json={
            "name": "Kelionė",
            "member_ids": user_ids
        }
    )
    assert group.status_code == 200
    group_id = group.json()["id"]

    expense = client.post(
        f"/tenants/{tenant_id}/groups/{group_id}/expenses",
        json={
            "paid_by": user_ids[0],
            "amount": "-10.00"
        }
    )

    assert expense.status_code == 400
    assert expense.json()["detail"] == "Suma turi būti didesnė už 0"

    balances_response = client.get(
        f"/tenants/{tenant_id}/groups/{group_id}/balances"
    )

    assert balances_response.status_code == 200

    data = balances_response.json()

    assert len(data["balances"]) == 3

    assert all(
        Decimal(person["balance"]) == Decimal("0.00")
        for person in data["balances"]
    )

    assert data["settlements"] == []