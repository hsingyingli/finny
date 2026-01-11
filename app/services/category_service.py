from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.categories.schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from app.exceptions import BadRequestError, NotFoundError
from app.models.category import Category, CategoryType
from app.repositories.category_repo import CategoryRepository


class CategoryService:
    """Service for category operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CategoryRepository(session)

    def _to_response(self, category: Category) -> CategoryResponse:
        return CategoryResponse(
            id=category.id,
            name=category.name,
            icon=category.icon,
            color=category.color,
            type=category.type,
            is_default=category.is_default,
            order=category.order,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )

    async def create(self, user_id: UUID, data: CategoryCreate) -> CategoryResponse:
        """Create a new category."""
        max_order = await self.repo.get_max_order(user_id, data.type)
        category = Category(
            user_id=user_id,
            name=data.name,
            icon=data.icon,
            color=data.color,
            type=data.type,
            order=max_order + 1,
        )
        category = await self.repo.create(category)
        return self._to_response(category)

    async def get_all(
        self,
        user_id: UUID,
        category_type: CategoryType | None = None,
    ) -> list[CategoryResponse]:
        """Get all categories for a user."""
        categories = await self.repo.get_by_user(user_id, category_type)
        return [self._to_response(c) for c in categories]

    async def get_by_id(self, user_id: UUID, category_id: UUID) -> CategoryResponse:
        """Get a single category."""
        category = await self.repo.get_by_id_and_user(category_id, user_id)
        if not category:
            raise NotFoundError("Category", str(category_id))
        return self._to_response(category)

    async def update(
        self,
        user_id: UUID,
        category_id: UUID,
        data: CategoryUpdate,
    ) -> CategoryResponse:
        """Update a category."""
        category = await self.repo.get_by_id_and_user(category_id, user_id)
        if not category:
            raise NotFoundError("Category", str(category_id))

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(category, key, value)
        category.updated_at = datetime.now(UTC)

        category = await self.repo.update(category)
        return self._to_response(category)

    async def delete(self, user_id: UUID, category_id: UUID) -> None:
        """Delete a category."""
        category = await self.repo.get_by_id_and_user(category_id, user_id)
        if not category:
            raise NotFoundError("Category", str(category_id))

        if category.is_default:
            raise BadRequestError("Cannot delete default category")

        await self.repo.delete(category)

    async def reorder(
        self,
        user_id: UUID,
        category_type: CategoryType,
        ordered_ids: list[UUID],
    ) -> list[CategoryResponse]:
        """Reorder categories."""
        categories = await self.repo.get_by_user(user_id, category_type)
        category_map = {c.id: c for c in categories}

        for i, cat_id in enumerate(ordered_ids):
            if cat_id in category_map:
                category_map[cat_id].order = i
                category_map[cat_id].updated_at = datetime.now(UTC)
                await self.repo.update(category_map[cat_id])

        # Fetch updated list
        updated = await self.repo.get_by_user(user_id, category_type)
        return [self._to_response(c) for c in updated]
