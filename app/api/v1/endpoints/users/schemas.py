from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.user import ThemeMode


class UserPreferencesResponse(BaseModel):
    """User preferences response."""

    theme: ThemeMode
    currency: str
    locale: str


class UserPreferencesUpdate(BaseModel):
    """Update user preferences."""

    theme: ThemeMode | None = None
    currency: str | None = None
    locale: str | None = None


class UserProfileResponse(BaseModel):
    """User profile response."""

    id: UUID
    email: str
    name: str
    is_active: bool
    theme: ThemeMode
    currency: str
    locale: str
    created_at: datetime
    updated_at: datetime
