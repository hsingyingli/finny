from enum import Enum

from sqlmodel import Field, SQLModel

from app.models.base import TimestampMixin, UUIDMixin


class ThemeMode(str, Enum):
    """Theme mode options."""

    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class User(UUIDMixin, TimestampMixin, SQLModel, table=True):
    """User model for authentication."""

    __tablename__ = "users"

    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    name: str = Field(max_length=100)
    is_active: bool = Field(default=True)

    # User preferences
    theme: ThemeMode = Field(default=ThemeMode.SYSTEM)
    currency: str = Field(default="TWD", max_length=10)
    locale: str = Field(default="zh-TW", max_length=10)
