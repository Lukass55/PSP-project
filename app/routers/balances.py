from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Account
from app.schemas import GroupBalancesResponse
from app.services.balance_service import calculate_group_balances

router = APIRouter(tags=["Balances"])


@router.get(
    "/groups/{group_id}/balances",
    response_model=GroupBalancesResponse
)
def get_group_balances(
    group_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    account_id = request.session.get("account_id")

    if account_id is None:
        raise HTTPException(401, "Turite prisijungti")

    account = db.query(Account).filter(
        Account.id == account_id
    ).first()

    if account is None:
        raise HTTPException(401, "Paskyra nerasta")

    return calculate_group_balances(
        db=db,
        account_id=account.id,
        group_id=group_id
    )
