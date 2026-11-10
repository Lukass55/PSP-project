from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Group, GroupMember, Expense, ExpenseShare
from app.schemas import ExpenseCreate


def create_expense(
    db: Session,
    tenant_id: int,
    group_id: int,
    expense: ExpenseCreate
):
    # Patikriname, ar grupė priklauso klientui
    group = db.query(Group).filter(
        Group.id == group_id,
        Group.tenant_id == tenant_id
    ).first()

    if group is None:
        raise HTTPException(status_code=404, detail="Grupė nerasta")

    # Gauname grupės narius nustatyta tvarka
    members = db.query(GroupMember).filter(
        GroupMember.group_id == group_id
    ).order_by(GroupMember.user_id).all()

    if not members:
        raise HTTPException(
            status_code=400,
            detail="Grupėje nėra žmonių"
        )

    member_ids = [member.user_id for member in members]

    # Mokėtojas privalo priklausyti grupei
    if expense.paid_by not in member_ids:
        raise HTTPException(
            status_code=400,
            detail="Mokėtojas nepriklauso šiai grupei"
        )

    # Tikriname išlaidos sumą
    amount = expense.amount

    if not amount.is_finite() or amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Suma turi būti didesnė už 0"
        )

    if amount > Decimal("99999999.99"):
        raise HTTPException(
            status_code=400,
            detail="Suma per didelė"
        )

    if amount != amount.quantize(Decimal("0.01")):
        raise HTTPException(
            status_code=400,
            detail="Suma gali turėti daugiausia 2 skaitmenis po kablelio"
        )

    # Paverčiame sumą centais
    cents = int(amount * 100)
    base_cents, remainder = divmod(cents, len(members))

    # Nustatome, nuo kurio žmogaus pradėti
    previous_expenses = db.query(Expense).filter(
        Expense.group_id == group_id
    ).count()

    start_index = previous_expenses % len(members)

    # Sukuriame išlaidą
    new_expense = Expense(
        group_id=group_id,
        paid_by=expense.paid_by,
        amount=amount
    )

    db.add(new_expense)
    db.flush()

    shares = []

    # Papildomus centus paskirstome paeiliui
    for index, member in enumerate(members):
        position = (index - start_index) % len(members)

        share_cents = base_cents + (1 if position < remainder else 0)
        share_amount = Decimal(share_cents) / 100

        db.add(
            ExpenseShare(
                expense_id=new_expense.id,
                user_id=member.user_id,
                amount=share_amount
            )
        )

        shares.append({
            "user_id": member.user_id,
            "amount": str(share_amount)
        })

    db.commit()
    db.refresh(new_expense)

    return {
        "id": new_expense.id,
        "group_id": group_id,
        "paid_by": expense.paid_by,
        "amount": str(amount),
        "shares": shares
    }