from enum import Enum
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.base import TimestampMixin, UUIDMixin


class CategoryType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class Category(UUIDMixin, TimestampMixin, SQLModel, table=True):
    """Category model for transaction categorization."""

    __tablename__ = "categories"

    user_id: UUID = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=100)
    icon: str = Field(max_length=50)
    color: str = Field(max_length=20)
    type: CategoryType
    is_default: bool = Field(default=False)
    order: int = Field(default=0)
