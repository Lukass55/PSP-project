from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Account, User, Group, GroupMember
from app.schemas import GroupCreate

router = APIRouter(tags=["Groups"])


def get_current_account(request: Request, db: Session):
    account_id = request.session.get("account_id")

    if account_id is None:
        raise HTTPException(401, "Turite prisijungti")

    account = db.query(Account).filter(
        Account.id == account_id
    ).first()

    if account is None:
        raise HTTPException(401, "Paskyra nerasta")

    return account


@router.get("/groups")
def get_groups(
    request: Request,
    db: Session = Depends(get_db)
):
    account = get_current_account(request, db)

    groups = db.query(Group).filter(
        Group.account_id == account.id
    ).order_by(Group.id).all()

    return [
        {"id": group.id, "name": group.name}
        for group in groups
    ]


@router.post("/groups", status_code=201)
def create_group(
    group: GroupCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    account = get_current_account(request, db)

    name = group.name.strip()

    if not name:
        raise HTTPException(
            400, "Grupės pavadinimas negali būti tuščias"
        )

    if account.user_id is None:
        raise HTTPException(
            400, "Paskyra neturi susieto vartotojo"
        )

    if len(group.member_ids) != len(set(group.member_ids)):
        raise HTTPException(
            400, "Tas pats žmogus negali kartotis"
        )

    # Kūrėją automatiškai įtraukiame į grupę
    member_ids = set(group.member_ids)
    member_ids.add(account.user_id)

    if len(member_ids) < 2:
        raise HTTPException(
            400, "Grupėje turi būti bent 2 žmonės"
        )

    # Patikriname, ar visi nariai priklauso paskyrai
    users = db.query(User).filter(
        User.id.in_(member_ids),
        User.account_id == account.id
    ).all()

    if len(users) != len(member_ids):
        raise HTTPException(
            400, "Pasirinkti žmonės nepriklauso jūsų paskyrai"
        )

    new_group = Group(
        name=name,
        account_id=account.id
    )

    db.add(new_group)
    db.flush()

    for user in users:
        db.add(GroupMember(
            group_id=new_group.id,
            user_id=user.id
        ))

    db.commit()
    db.refresh(new_group)

    return {
        "id": new_group.id,
        "name": new_group.name,
        "account_id": account.id,
        "member_ids": sorted(member_ids)
    }
