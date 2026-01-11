from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.budgets.schemas import (
    BudgetCreate,
    BudgetResponse,
    BudgetUpdate,
)
from app.exceptions import NotFoundError
from app.models.budget import Budget
from app.repositories.budget_repo import BudgetRepository


class BudgetService:
    """Service for budget operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = BudgetRepository(session)

    def _to_response(self, budget: Budget) -> BudgetResponse:
        return BudgetResponse(
            id=budget.id,
            category_id=budget.category_id,
            amount=budget.amount,
            period=budget.period,
            start_date=budget.start_date,
            is_active=budget.is_active,
            created_at=budget.created_at,
            updated_at=budget.updated_at,
        )

    async def create(self, user_id: UUID, data: BudgetCreate) -> BudgetResponse:
        """Create a new budget."""
        budget = Budget(
            user_id=user_id,
            category_id=data.category_id,
            amount=data.amount,
            period=data.period,
            start_date=data.start_date or date.today(),
        )
        budget = await self.repo.create(budget)
        return self._to_response(budget)

    async def get_all(self, user_id: UUID) -> list[BudgetResponse]:
        """Get all active budgets for a user."""
        budgets = await self.repo.get_by_user(user_id, active_only=True)
        return [self._to_response(b) for b in budgets]

    async def get_by_id(self, user_id: UUID, budget_id: UUID) -> BudgetResponse:
        """Get a single budget."""
        budget = await self.repo.get_by_id_and_user(budget_id, user_id)
        if not budget:
            raise NotFoundError("Budget", str(budget_id))
        return self._to_response(budget)

    async def get_by_category(
        self, user_id: UUID, category_id: UUID
    ) -> BudgetResponse | None:
        """Get budget for a specific category."""
        budget = await self.repo.get_by_category(category_id, user_id)
        if not budget:
            return None
        return self._to_response(budget)

    async def update(
        self,
        user_id: UUID,
        budget_id: UUID,
        data: BudgetUpdate,
    ) -> BudgetResponse:
        """Update a budget."""
        budget = await self.repo.get_by_id_and_user(budget_id, user_id)
        if not budget:
            raise NotFoundError("Budget", str(budget_id))

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(budget, key, value)
        budget.updated_at = datetime.now(UTC)

        budget = await self.repo.update(budget)
        return self._to_response(budget)

    async def deactivate(self, user_id: UUID, budget_id: UUID) -> BudgetResponse:
        """Deactivate a budget (soft delete)."""
        budget = await self.repo.get_by_id_and_user(budget_id, user_id)
        if not budget:
            raise NotFoundError("Budget", str(budget_id))

        budget.is_active = False
        budget.updated_at = datetime.now(UTC)
        budget = await self.repo.update(budget)
        return self._to_response(budget)
