from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TagCreate(BaseModel):
    name: str
    color: str | None = "#6B7280"


class TagUpdate(BaseModel):
    name: str | None = None
    color: str | None = None


class TagResponse(BaseModel):
    id: UUID
    name: str
    color: str
    usage_count: int
    created_at: datetime
    updated_at: datetime
