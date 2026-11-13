from decimal import Decimal

def test_normal_expense(client, create_group):
    data = create_group()

    group_id = data["group_id"]
    payer_id = data["account"]["user_id"]

    response = client.post(
        f"/groups/{group_id}/expenses",
        json={
            "paid_by": payer_id,
            "amount": "60.00"
        }
    )

    assert response.status_code == 200, response.text

    expense = response.json()

    assert Decimal(expense["amount"]) == Decimal("60.00")
    assert len(expense["shares"]) == 3

    shares = [
        Decimal(share["amount"])
        for share in expense["shares"]
    ]

    assert shares == [
        Decimal("20.00"),
        Decimal("20.00"),
        Decimal("20.00")
    ]

    balances_response = client.get(
        f"/groups/{group_id}/balances"
    )

    assert balances_response.status_code == 200

    balances = balances_response.json()["balances"]

    assert len(balances) == 3

    payer = next(
        person for person in balances
        if person["user_id"] == payer_id
    )

    assert Decimal(payer["total_paid"]) == Decimal("60.00")
    assert Decimal(payer["total_share"]) == Decimal("20.00")
    assert Decimal(payer["balance"]) == Decimal("40.00")
