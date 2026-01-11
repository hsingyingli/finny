from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import TIMESTAMP
from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    """Mixin for timestamp fields."""

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
        sa_type=TIMESTAMP(timezone=True),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
        sa_type=TIMESTAMP(timezone=True),
        sa_column_kwargs={"onupdate": lambda: datetime.now(UTC)},
    )


class UUIDMixin(SQLModel):
    """Mixin for UUID primary key."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
