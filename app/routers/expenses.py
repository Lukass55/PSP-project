from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Account, Group, Expense, ExpenseShare
from app.schemas import ExpenseCreate
from app.services.expense_service import (
    create_expense as create_expense_service
)

router = APIRouter(tags=["Expenses"])


def get_current_account(request: Request, db: Session):
    account_id = request.session.get("account_id")

    if account_id is None:
        raise HTTPException(401, "Turite prisijungti")

    account = db.query(Account).filter(
        Account.id == account_id
    ).first()

    if account is None:
        raise HTTPException(401, "Paskyra nerasta")

    return account


@router.post("/groups/{group_id}/expenses")
def create_expense(
    group_id: int,
    expense: ExpenseCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    account = get_current_account(request, db)

    return create_expense_service(
        db=db,
        account_id=account.id,
        group_id=group_id,
        expense=expense
    )


@router.delete("/groups/{group_id}/expenses")
def reset_group_expenses(
    group_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    account = get_current_account(request, db)

    group = db.query(Group).filter(
        Group.id == group_id,
        Group.account_id == account.id
    ).first()

    if group is None:
        raise HTTPException(404, "Grupė nerasta")

    expense_ids = [
        expense.id
        for expense in db.query(Expense).filter(
            Expense.group_id == group_id
        ).all()
    ]

    try:
        if expense_ids:
            db.query(ExpenseShare).filter(
                ExpenseShare.expense_id.in_(expense_ids)
            ).delete(synchronize_session=False)

            db.query(Expense).filter(
                Expense.id.in_(expense_ids)
            ).delete(synchronize_session=False)

        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "message": "Grupės išlaidos išvalytos",
        "deleted_expenses": len(expense_ids)
    }
