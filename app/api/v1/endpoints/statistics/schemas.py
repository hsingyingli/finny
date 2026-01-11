from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class MonthlySummaryResponse(BaseModel):
    """Monthly summary response."""

    total_income: Decimal
    total_expense: Decimal
    balance: Decimal
    transaction_count: int


class CategorySpending(BaseModel):
    """Category spending breakdown."""

    category_id: UUID
    category_name: str
    category_icon: str | None
    category_color: str | None
    amount: Decimal
    percentage: Decimal
    transaction_count: int


class CategoryBreakdownResponse(BaseModel):
    """Category breakdown response."""

    total: Decimal
    categories: list[CategorySpending]
