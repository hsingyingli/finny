from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.models.account import AccountType


class AccountCreate(BaseModel):
    name: str
    type: AccountType = AccountType.CASH
    initial_balance: Decimal = Decimal("0")
    icon: str | None = None
    color: str | None = None


class AccountUpdate(BaseModel):
    name: str | None = None
    type: AccountType | None = None
    icon: str | None = None
    color: str | None = None


class AccountBalanceUpdate(BaseModel):
    delta: Decimal


class AccountResponse(BaseModel):
    id: UUID
    name: str
    type: AccountType
    balance: Decimal
    initial_balance: Decimal
    icon: str | None
    color: str | None
    is_default: bool
    is_archived: bool
    order: int
    created_at: datetime
    updated_at: datetime


class TotalBalanceResponse(BaseModel):
    total_balance: Decimal
