from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.category import CategoryType


class CategoryCreate(BaseModel):
    name: str
    icon: str | None = "tag"
    color: str | None = "#6B7280"
    type: CategoryType


class CategoryUpdate(BaseModel):
    name: str | None = None
    icon: str | None = None
    color: str | None = None


class CategoryReorder(BaseModel):
    type: CategoryType
    ordered_ids: list[UUID]


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    icon: str | None
    color: str | None
    type: CategoryType
    is_default: bool
    order: int
    created_at: datetime
    updated_at: datetime
