from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

from app.database import get_db
from app.models import Account, Tenant

from fastapi import Request

router = APIRouter(tags=["Authentication"])

password_hash = PasswordHash.recommended()


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)


@router.post("/auth/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    username = data.username.strip()

    if len(username) < 3:
        raise HTTPException(
            status_code=400,
            detail="Naudotojo vardas turi turėti bent 3 simbolius"
        )

    existing = db.query(Account).filter(
        Account.username == username
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Toks naudotojo vardas jau užimtas"
        )

    tenant = Tenant(name=f"{username} erdvė")
    db.add(tenant)
    db.flush()

    account = Account(
        username=username,
        password_hash=password_hash.hash(data.password),
        tenant_id=tenant.id
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return {
        "message": "Paskyra sėkmingai sukurta",
        "account_id": account.id,
        "username": account.username
    }

class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/auth/login")
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    account = (
        db.query(Account)
        .filter(Account.username == data.username)
        .first()
    )

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
        "tenant_id": account.tenant_id
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
        "tenant_id": account.tenant_id
    }


@router.post("/auth/logout")
def logout(request: Request):
    request.session.clear()
    return {"message": "Sėkmingai atsijungta"}