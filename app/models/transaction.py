import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.base import TimestampMixin, UUIDMixin


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class Transaction(UUIDMixin, TimestampMixin, SQLModel, table=True):
    """Transaction model for financial records."""

    __tablename__ = "transactions"

    user_id: UUID = Field(foreign_key="users.id", index=True)
    amount: Decimal = Field(max_digits=15, decimal_places=2)
    type: TransactionType
    category_id: UUID | None = Field(
        default=None, foreign_key="categories.id", index=True
    )
    account_id: UUID = Field(foreign_key="accounts.id", index=True)
    to_account_id: UUID | None = Field(default=None, foreign_key="accounts.id")
    date: datetime.date = Field(index=True)
    note: str | None = Field(default=None, max_length=500)


class TransactionTag(SQLModel, table=True):
    """Many-to-many relationship between transactions and tags."""

    __tablename__ = "transaction_tags"

    transaction_id: UUID = Field(foreign_key="transactions.id", primary_key=True)
    tag_id: UUID = Field(foreign_key="tags.id", primary_key=True)
