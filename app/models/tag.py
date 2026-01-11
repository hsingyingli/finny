from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.base import TimestampMixin, UUIDMixin


class Tag(UUIDMixin, TimestampMixin, SQLModel, table=True):
    """Tag model for transaction tagging."""

    __tablename__ = "tags"

    user_id: UUID = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=50, index=True)
    color: str = Field(default="#6B7280", max_length=20)
    usage_count: int = Field(default=0)
