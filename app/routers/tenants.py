from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Tenant
from app.schemas import TenantCreate


router = APIRouter(tags=["Tenants"])

@router.get("/tenants")
def get_tenants(db: Session = Depends(get_db)):
    tenants = db.query(Tenant).order_by(Tenant.id).all()

    return [
        {
            "id": tenant.id,
            "name": tenant.name
        }
        for tenant in tenants
    ]
@router.post("/tenants")
def create_tenant(tenant: TenantCreate, db: Session = Depends(get_db)):
    name = tenant.name.strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Kliento pavadinimas negali būti tuščias"
        )

    new_tenant = Tenant(name=name)

    db.add(new_tenant)
    db.commit()
    db.refresh(new_tenant)

    return {
        "id": new_tenant.id,
        "name": new_tenant.name
    }