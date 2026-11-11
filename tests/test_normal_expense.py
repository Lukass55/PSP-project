from decimal import Decimal


def test_normal_expense(client):
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
            "amount": "60.00"
        }
    )

    assert expense.status_code == 200

    data = expense.json()

    assert Decimal(data["amount"]) == Decimal("60.00")
    assert len(data["shares"]) == 3

    assert all(
        Decimal(share["amount"]) == Decimal("20.00")
        for share in data["shares"]
    )