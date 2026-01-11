from decimal import Decimal
from enum import Enum
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.base import TimestampMixin, UUIDMixin


class AccountType(str, Enum):
    CASH = "cash"
    BANK = "bank"
    CREDIT_CARD = "credit_card"
    INVESTMENT = "investment"
    OTHER = "other"


class Account(UUIDMixin, TimestampMixin, SQLModel, table=True):
    """Account model for managing user accounts."""

    __tablename__ = "accounts"

    user_id: UUID = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=100)
    type: AccountType = Field(default=AccountType.CASH)
    balance: Decimal = Field(default=Decimal("0"), max_digits=15, decimal_places=2)
    initial_balance: Decimal = Field(
        default=Decimal("0"), max_digits=15, decimal_places=2
    )
    icon: str | None = Field(default=None, max_length=50)
    color: str | None = Field(default=None, max_length=20)
    is_default: bool = Field(default=False)
    is_archived: bool = Field(default=False)
    order: int = Field(default=0)
