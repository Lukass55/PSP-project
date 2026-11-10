from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ExpenseCreate
from app.services.expense_service import create_expense as create_expense_service


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