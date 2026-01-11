import datetime
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.v1.endpoints.statistics.schemas import (
    CategoryBreakdownResponse,
    MonthlySummaryResponse,
)
from app.dependencies import CurrentUserDep, SessionDep
from app.models.transaction import TransactionType
from app.schemas.common import ApiResponse
from app.services.statistics_service import StatisticsService

router = APIRouter()


@router.get("/summary")
async def get_summary(
    session: SessionDep,
    current_user_id: CurrentUserDep,
    start_date: Annotated[datetime.date, Query(alias="startDate")],
    end_date: Annotated[datetime.date, Query(alias="endDate")],
) -> ApiResponse[MonthlySummaryResponse]:
    """Get income/expense summary for a date range."""
    service = StatisticsService(session)
    summary = await service.get_monthly_summary(current_user_id, start_date, end_date)
    return ApiResponse(data=summary)


@router.get("/category-breakdown")
async def get_category_breakdown(
    session: SessionDep,
    current_user_id: CurrentUserDep,
    start_date: Annotated[datetime.date, Query(alias="startDate")],
    end_date: Annotated[datetime.date, Query(alias="endDate")],
    type: Annotated[TransactionType, Query()] = TransactionType.EXPENSE,
) -> ApiResponse[CategoryBreakdownResponse]:
    """Get spending breakdown by category for a date range."""
    service = StatisticsService(session)
    breakdown = await service.get_category_breakdown(
        current_user_id, start_date, end_date, type
    )
    return ApiResponse(data=breakdown)
