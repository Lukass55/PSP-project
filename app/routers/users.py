from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Account, User
from app.schemas import UserCreate

router = APIRouter(tags=["Users"])


def get_current_account(request: Request, db: Session):
    account_id = request.session.get("account_id")

    if account_id is None:
        raise HTTPException(
            status_code=401,
            detail="Turite prisijungti"
        )

    account = db.query(Account).filter(
        Account.id == account_id
    ).first()

    if account is None:
        raise HTTPException(
            status_code=401,
            detail="Paskyra nerasta"
        )

    return account


@router.get("/users")
def get_users(
    request: Request,
    db: Session = Depends(get_db)
):
    account = get_current_account(request, db)

    users = db.query(User).filter(
        User.account_id == account.id
    ).order_by(User.id).all()

    return [
        {
            "id": user.id,
            "name": user.name,
            "surname": user.surname
        }
        for user in users
    ]


@router.post("/users", status_code=201)
def create_user(
    user: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    account = get_current_account(request, db)

    name = user.name.strip()
    surname = user.surname.strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Vardas negali būti tuščias"
        )

    if not surname:
        raise HTTPException(
            status_code=400,
            detail="Pavardė negali būti tuščia"
        )

    new_user = User(
        name=name,
        surname=surname,
        account_id=account.id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "name": new_user.name,
        "surname": new_user.surname,
        "account_id": new_user.account_id
    }
