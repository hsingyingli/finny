from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from app.api.v1.endpoints.categories.schemas import (
    CategoryCreate,
    CategoryReorder,
    CategoryResponse,
    CategoryUpdate,
)
from app.dependencies import CurrentUserDep, SessionDep
from app.models.category import CategoryType
from app.schemas.common import ApiResponse, EmptyResponse
from app.services.category_service import CategoryService

router = APIRouter()


@router.post("")
async def create_category(
    request: CategoryCreate,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[CategoryResponse]:
    """Create a new category."""
    service = CategoryService(session)
    category = await service.create(current_user_id, request)
    return ApiResponse(data=category, message="Category created successfully")


@router.get("")
async def get_categories(
    session: SessionDep,
    current_user_id: CurrentUserDep,
    type: Annotated[CategoryType | None, Query()] = None,
) -> ApiResponse[list[CategoryResponse]]:
    """Get all categories."""
    service = CategoryService(session)
    categories = await service.get_all(current_user_id, type)
    return ApiResponse(data=categories)


@router.put("/reorder")
async def reorder_categories(
    request: CategoryReorder,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[list[CategoryResponse]]:
    """Reorder categories."""
    service = CategoryService(session)
    categories = await service.reorder(
        current_user_id, request.type, request.ordered_ids
    )
    return ApiResponse(data=categories, message="Categories reordered successfully")


@router.get("/{category_id}")
async def get_category(
    category_id: UUID,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[CategoryResponse]:
    """Get a single category."""
    service = CategoryService(session)
    category = await service.get_by_id(current_user_id, category_id)
    return ApiResponse(data=category)


@router.put("/{category_id}")
async def update_category(
    category_id: UUID,
    request: CategoryUpdate,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[CategoryResponse]:
    """Update a category."""
    service = CategoryService(session)
    category = await service.update(current_user_id, category_id, request)
    return ApiResponse(data=category, message="Category updated successfully")


@router.delete("/{category_id}")
async def delete_category(
    category_id: UUID,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[EmptyResponse]:
    """Delete a category."""
    service = CategoryService(session)
    await service.delete(current_user_id, category_id)
    return ApiResponse(data=EmptyResponse(), message="Category deleted successfully")
