from decimal import Decimal

def test_boundary_expense(client, create_group):
    data = create_group()

    group_id = data["group_id"]
    payer_id = data["account"]["user_id"]

    response = client.post(
        f"/groups/{group_id}/expenses",
        json={
            "paid_by": payer_id,
            "amount": "100.00"
        }
    )

    assert response.status_code == 200, response.text

    expense = response.json()

    shares = [
        Decimal(share["amount"])
        for share in expense["shares"]
    ]

    assert sorted(shares) == sorted([
        Decimal("33.34"),
        Decimal("33.33"),
        Decimal("33.33")
    ])

    assert sum(shares) == Decimal("100.00")

    assert len(shares) == 3

    balances_response = client.get(
        f"/groups/{group_id}/balances"
    )

    assert balances_response.status_code == 200

    balances = balances_response.json()["balances"]

    total_balances = sum(
        Decimal(person["balance"])
        for person in balances
    )

    assert total_balances == Decimal("0.00")
