from decimal import Decimal

def test_invalid_expense(client, create_group):
    data = create_group()

    group_id = data["group_id"]
    payer_id = data["account"]["user_id"]

    response = client.post(
        f"/groups/{group_id}/expenses",
        json={
            "paid_by": payer_id,
            "amount": "-10.00"
        }
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Suma turi būti didesnė už 0"
    )

    balances_response = client.get(
        f"/groups/{group_id}/balances"
    )

    assert balances_response.status_code == 200

    balances = balances_response.json()["balances"]

    assert len(balances) == 3

    assert all(
        Decimal(person["total_paid"]) == Decimal("0.00")
        for person in balances
    )

    assert all(
        Decimal(person["balance"]) == Decimal("0.00")
        for person in balances
    )

    assert balances_response.json()["settlements"] == []
