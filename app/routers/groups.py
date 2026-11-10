from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Tenant, User, Group, GroupMember
from app.schemas import GroupCreate


router = APIRouter(tags=["Groups"])


@router.post("/tenants/{tenant_id}/groups")
def create_group(
    tenant_id: int,
    group: GroupCreate,
    db: Session = Depends(get_db)
):
    # Patikriname, ar klientas egzistuoja
    tenant = db.query(Tenant).filter(
        Tenant.id == tenant_id
    ).first()

    if tenant is None:
        raise HTTPException(
            status_code=404,
            detail="Klientas nerastas"
        )

    name = group.name.strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Grupės pavadinimas negali būti tuščias"
        )

    # Grupėje turi būti bent 2 skirtingi žmonės
    if len(group.member_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="Grupėje turi būti bent 2 žmonės"
        )

    if len(group.member_ids) != len(set(group.member_ids)):
        raise HTTPException(
            status_code=400,
            detail="Tas pats žmogus negali kartotis"
        )

    # Visi nariai turi priklausyti tam pačiam klientui
    users = db.query(User).filter(
        User.id.in_(group.member_ids),
        User.tenant_id == tenant_id
    ).all()

    if len(users) != len(group.member_ids):
        raise HTTPException(
            status_code=400,
            detail="Visi grupės nariai turi būti pridėti prie šio kliento"
        )

    # Sukuriame grupę
    new_group = Group(
        name=name,
        tenant_id=tenant_id
    )

    db.add(new_group)
    db.flush()

    # Pridedame grupės narius
    for user in users:
        db.add(
            GroupMember(
                group_id=new_group.id,
                user_id=user.id
            )
        )

    db.commit()
    db.refresh(new_group)

    return {
        "id": new_group.id,
        "name": new_group.name,
        "tenant_id": new_group.tenant_id,
        "member_ids": group.member_ids
    }