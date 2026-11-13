from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Group, GroupMember, User, Expense, ExpenseShare


def calculate_group_balances(
    db: Session,
    account_id: int,
    group_id: int
):
    group = db.query(Group).filter(
        Group.id == group_id,
        Group.account_id == account_id
    ).first()

    if group is None:
        raise HTTPException(404, "Grupė nerasta")

    members = db.query(User).join(
        GroupMember,
        User.id == GroupMember.user_id
    ).filter(
        GroupMember.group_id == group_id,
        User.account_id == account_id
    ).order_by(User.id).all()

    expenses = db.query(Expense).filter(
        Expense.group_id == group_id
    ).all()

    balances = []

    for member in members:
        total_paid = Decimal("0.00")
        total_share = Decimal("0.00")

        for expense in expenses:
            if expense.paid_by == member.id:
                total_paid += expense.amount

            share = db.query(ExpenseShare).filter(
                ExpenseShare.expense_id == expense.id,
                ExpenseShare.user_id == member.id
            ).first()

            if share is not None:
                total_share += share.amount

        balance = total_paid - total_share

        balances.append({
            "user_id": member.id,
            "name": member.name,
            "surname": member.surname,
            "total_paid": str(total_paid),
            "total_share": str(total_share),
            "balance": str(balance)
        })

    settlements = calculate_settlements(balances)

    return {
        "group_id": group_id,
        "group_name": group.name,
        "balances": balances,
        "settlements": settlements
    }


def calculate_settlements(balances: list[dict]) -> list[dict]:
    debtors = []
    creditors = []

    for person in balances:
        balance = Decimal(str(person["balance"]))

        if balance < 0:
            debtors.append({
                "user_id": person["user_id"],
                "name": person["name"],
                "surname": person["surname"],
                "amount": -balance
            })

        elif balance > 0:
            creditors.append({
                "user_id": person["user_id"],
                "name": person["name"],
                "surname": person["surname"],
                "amount": balance
            })

    settlements = []
    debtor_index = 0
    creditor_index = 0

    while (
        debtor_index < len(debtors)
        and creditor_index < len(creditors)
    ):
        debtor = debtors[debtor_index]
        creditor = creditors[creditor_index]

        amount = min(
            debtor["amount"],
            creditor["amount"]
        )

        settlements.append({
            "from_user_id": debtor["user_id"],
            "from_name": debtor["name"],
            "from_surname": debtor["surname"],
            "to_user_id": creditor["user_id"],
            "to_name": creditor["name"],
            "to_surname": creditor["surname"],
            "amount": str(amount)
        })

        debtor["amount"] -= amount
        creditor["amount"] -= amount

        if debtor["amount"] == 0:
            debtor_index += 1

        if creditor["amount"] == 0:
            creditor_index += 1

    return settlements
