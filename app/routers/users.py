from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Tenant, User
from app.schemas import UserCreate


router = APIRouter(tags=["Users"])

@router.get("/tenants/{tenant_id}/users")
def get_users(tenant_id: int, db: Session = Depends(get_db)):
    users = (
        db.query(User)
        .filter(User.tenant_id == tenant_id)
        .order_by(User.id)
        .all()
    )

    return [
        {"id": user.id, "name": user.name, "surname": user.surname}
        for user in users
    ]

@router.post("/tenants/{tenant_id}/users")
def create_user(
    tenant_id: int,
    user: UserCreate,
    db: Session = Depends(get_db)
):
    tenant = db.query(Tenant).filter(
        Tenant.id == tenant_id
    ).first()

    if tenant is None:
        raise HTTPException(
            status_code=404,
            detail="Klientas nerastas"
        )

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
        tenant_id=tenant_id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "name": new_user.name,
        "surname": new_user.surname,
        "tenant_id": new_user.tenant_id
    }