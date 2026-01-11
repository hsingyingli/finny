import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.base import TimestampMixin, UUIDMixin


class BudgetPeriod(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class Budget(UUIDMixin, TimestampMixin, SQLModel, table=True):
    """Budget model for expense tracking limits."""

    __tablename__ = "budgets"

    user_id: UUID = Field(foreign_key="users.id", index=True)
    category_id: UUID = Field(foreign_key="categories.id", index=True)
    amount: Decimal = Field(max_digits=15, decimal_places=2)
    period: BudgetPeriod
    start_date: datetime.date = Field(default_factory=datetime.date.today)
    is_active: bool = Field(default=True)
