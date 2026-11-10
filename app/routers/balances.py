from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import GroupBalancesResponse
from app.services.balance_service import calculate_group_balances


router = APIRouter(tags=["Balances"])


@router.get(
    "/tenants/{tenant_id}/groups/{group_id}/balances",
    response_model=GroupBalancesResponse
)
def get_group_balances(
    tenant_id: int,
    group_id: int,
    db: Session = Depends(get_db)
):
    return calculate_group_balances(
        db=db,
        tenant_id=tenant_id,
        group_id=group_id
    )