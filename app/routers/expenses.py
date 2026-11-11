from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ExpenseCreate
from app.services.expense_service import create_expense as create_expense_service

from fastapi import HTTPException
from app.models import Group, Expense, ExpenseShare

router = APIRouter(tags=["Expenses"])



@router.post("/tenants/{tenant_id}/groups/{group_id}/expenses")
def create_expense(
    tenant_id: int,
    group_id: int,
    expense: ExpenseCreate,
    db: Session = Depends(get_db)
):
    return create_expense_service(
        db=db,
        tenant_id=tenant_id,
        group_id=group_id,
        expense=expense
    )
@router.delete("/tenants/{tenant_id}/groups/{group_id}/expenses")
def reset_group_expenses(
    tenant_id: int,
    group_id: int,
    db: Session = Depends(get_db)
):
    group = (
        db.query(Group)
        .filter(
            Group.id == group_id,
            Group.tenant_id == tenant_id
        )
        .first()
    )

    if group is None:
        raise HTTPException(
            status_code=404,
            detail="Grupė nerasta"
        )

    expense_ids = [
        expense.id
        for expense in db.query(Expense)
        .filter(Expense.group_id == group_id)
        .all()
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