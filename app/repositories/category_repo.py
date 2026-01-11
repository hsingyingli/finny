from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category, CategoryType
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """Repository for Category model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Category)

    async def get_by_user(
        self,
        user_id: UUID,
        category_type: CategoryType | None = None,
    ) -> list[Category]:
        """Get all categories for a user."""
        query = select(Category).where(Category.user_id == user_id)
        if category_type:
            query = query.where(Category.type == category_type)
        query = query.order_by(Category.order, Category.created_at)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id_and_user(self, id: UUID, user_id: UUID) -> Category | None:
        """Get a category by ID and user."""
        result = await self.session.execute(
            select(Category).where(Category.id == id, Category.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_max_order(self, user_id: UUID, category_type: CategoryType) -> int:
        """Get the maximum order value for a user's categories of a type."""
        result = await self.session.execute(
            select(func.coalesce(func.max(Category.order), -1)).where(
                Category.user_id == user_id,
                Category.type == category_type,
            )
        )
        return result.scalar_one() or -1
