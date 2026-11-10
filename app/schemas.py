from decimal import Decimal

from pydantic import BaseModel, Field


class TenantCreate(BaseModel):
    name: str = Field(max_length=100)


class UserCreate(BaseModel):
    name: str = Field(max_length=100)
    surname: str = Field(max_length=100)


class GroupCreate(BaseModel):
    name: str = Field(max_length=100)
    member_ids: list[int]


class ExpenseCreate(BaseModel):
    paid_by: int
    amount: Decimal


class BalanceResponse(BaseModel):
    user_id: int
    name: str
    surname: str
    total_paid: Decimal
    total_share: Decimal
    balance: Decimal


class SettlementResponse(BaseModel):
    from_user_id: int
    from_name: str
    from_surname: str
    to_user_id: int
    to_name: str
    to_surname: str
    amount: Decimal


class GroupBalancesResponse(BaseModel):
    group_id: int
    group_name: str
    balances: list[BalanceResponse]
    settlements: list[SettlementResponse]