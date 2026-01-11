from uuid import UUID

from fastapi import APIRouter

from app.api.v1.endpoints.budgets.schemas import (
    BudgetCreate,
    BudgetResponse,
    BudgetUpdate,
)
from app.dependencies import CurrentUserDep, SessionDep
from app.exceptions import NotFoundError
from app.schemas.common import ApiResponse
from app.services.budget_service import BudgetService

router = APIRouter()


@router.post("")
async def create_budget(
    request: BudgetCreate,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[BudgetResponse]:
    """Create a new budget."""
    service = BudgetService(session)
    budget = await service.create(current_user_id, request)
    return ApiResponse(data=budget, message="Budget created successfully")


@router.get("")
async def get_budgets(
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[list[BudgetResponse]]:
    """Get all active budgets."""
    service = BudgetService(session)
    budgets = await service.get_all(current_user_id)
    return ApiResponse(data=budgets)


@router.get("/category/{category_id}")
async def get_budget_by_category(
    category_id: UUID,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[BudgetResponse]:
    """Get budget for a specific category."""
    service = BudgetService(session)
    budget = await service.get_by_category(current_user_id, category_id)
    if not budget:
        raise NotFoundError("Budget for category", str(category_id))
    return ApiResponse(data=budget)


@router.get("/{budget_id}")
async def get_budget(
    budget_id: UUID,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[BudgetResponse]:
    """Get a single budget."""
    service = BudgetService(session)
    budget = await service.get_by_id(current_user_id, budget_id)
    return ApiResponse(data=budget)


@router.put("/{budget_id}")
async def update_budget(
    budget_id: UUID,
    request: BudgetUpdate,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[BudgetResponse]:
    """Update a budget."""
    service = BudgetService(session)
    budget = await service.update(current_user_id, budget_id, request)
    return ApiResponse(data=budget, message="Budget updated successfully")


@router.delete("/{budget_id}")
async def deactivate_budget(
    budget_id: UUID,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[BudgetResponse]:
    """Deactivate a budget (soft delete)."""
    service = BudgetService(session)
    budget = await service.deactivate(current_user_id, budget_id)
    return ApiResponse(data=budget, message="Budget deactivated successfully")
