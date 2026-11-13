from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

from app.database import get_db
from app.models import Account, User

router = APIRouter(tags=["Authentication"])
password_hash = PasswordHash.recommended()


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    name: str = Field(min_length=1, max_length=50)
    surname: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/auth/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    username = data.username.strip()
    name = data.name.strip()
    surname = data.surname.strip()

    if len(username) < 3 or not name or not surname:
        raise HTTPException(
            status_code=400,
            detail="Patikrinkite naudotojo vardą, vardą ir pavardę"
        )

    existing = db.query(Account).filter(
        Account.username == username
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Toks naudotojo vardas jau užimtas"
        )

    account = Account(
        username=username,
        password_hash=password_hash.hash(data.password),
        name=name,
        surname=surname
    )

    db.add(account)
    db.flush()

    user = User(
        name=name,
        surname=surname,
        account_id=account.id
    )

    db.add(user)
    db.flush()

    account.user_id = user.id

    db.commit()
    db.refresh(account)

    return {
        "message": "Paskyra sėkmingai sukurta",
        "account_id": account.id,
        "username": account.username,
        "user_id": account.user_id
    }


@router.post("/auth/login")
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    account = db.query(Account).filter(
        Account.username == data.username
    ).first()

    if account is None or not password_hash.verify(
        data.password, account.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Neteisingas naudotojo vardas arba slaptažodis"
        )

    request.session.clear()
    request.session["account_id"] = account.id

    return {
        "message": "Prisijungimas sėkmingas",
        "account_id": account.id,
        "username": account.username,
        "user_id": account.user_id
    }


@router.get("/auth/me")
def get_current_account(
    request: Request,
    db: Session = Depends(get_db)
):
    account_id = request.session.get("account_id")

    if account_id is None:
        raise HTTPException(
            status_code=401,
            detail="Neprisijungęs naudotojas"
        )

    account = db.query(Account).filter(
        Account.id == account_id
    ).first()

    if account is None:
        request.session.clear()
        raise HTTPException(
            status_code=401,
            detail="Paskyra nerasta"
        )

    return {
        "id": account.id,
        "username": account.username,
        "name": account.name,
        "surname": account.surname,
        "user_id": account.user_id
    }


@router.post("/auth/logout")
def logout(request: Request):
    request.session.clear()
    return {"message": "Sėkmingai atsijungta"}
