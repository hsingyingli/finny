from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import Budget
from app.repositories.base import BaseRepository


class BudgetRepository(BaseRepository[Budget]):
    """Repository for Budget model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Budget)

    async def get_by_user(
        self, user_id: UUID, active_only: bool = True
    ) -> list[Budget]:
        """Get all budgets for a user."""
        query = select(Budget).where(Budget.user_id == user_id)
        if active_only:
            query = query.where(Budget.is_active == True)  # noqa: E712
        query = query.order_by(Budget.created_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id_and_user(self, id: UUID, user_id: UUID) -> Budget | None:
        """Get a budget by ID and user."""
        result = await self.session.execute(
            select(Budget).where(Budget.id == id, Budget.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_category(self, category_id: UUID, user_id: UUID) -> Budget | None:
        """Get active budget for a category."""
        result = await self.session.execute(
            select(Budget).where(
                Budget.category_id == category_id,
                Budget.user_id == user_id,
                Budget.is_active == True,  # noqa: E712
            )
        )
        return result.scalar_one_or_none()
