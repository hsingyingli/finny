from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.statistics.schemas import (
    CategoryBreakdownResponse,
    CategorySpending,
    MonthlySummaryResponse,
)
from app.models.category import Category
from app.models.transaction import Transaction, TransactionType


class StatisticsService:
    """Service for statistics operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_monthly_summary(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date,
    ) -> MonthlySummaryResponse:
        """Get monthly income/expense summary."""
        # Get income total
        income_result = await self.session.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0))
            .where(Transaction.user_id == user_id)
            .where(Transaction.type == TransactionType.INCOME)
            .where(Transaction.date >= start_date)
            .where(Transaction.date <= end_date)
        )
        total_income = income_result.scalar() or Decimal(0)

        # Get expense total
        expense_result = await self.session.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0))
            .where(Transaction.user_id == user_id)
            .where(Transaction.type == TransactionType.EXPENSE)
            .where(Transaction.date >= start_date)
            .where(Transaction.date <= end_date)
        )
        total_expense = expense_result.scalar() or Decimal(0)

        # Get transaction count
        count_result = await self.session.execute(
            select(func.count(Transaction.id))
            .where(Transaction.user_id == user_id)
            .where(Transaction.date >= start_date)
            .where(Transaction.date <= end_date)
        )
        transaction_count = count_result.scalar() or 0

        return MonthlySummaryResponse(
            total_income=total_income,
            total_expense=total_expense,
            balance=total_income - total_expense,
            transaction_count=transaction_count,
        )

    async def get_category_breakdown(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date,
        transaction_type: TransactionType = TransactionType.EXPENSE,
    ) -> CategoryBreakdownResponse:
        """Get spending breakdown by category."""
        # Get spending by category
        result = await self.session.execute(
            select(
                Transaction.category_id,
                Category.name,
                Category.icon,
                Category.color,
                func.sum(Transaction.amount).label("amount"),
                func.count(Transaction.id).label("count"),
            )
            .join(Category, Transaction.category_id == Category.id)
            .where(Transaction.user_id == user_id)
            .where(Transaction.type == transaction_type)
            .where(Transaction.date >= start_date)
            .where(Transaction.date <= end_date)
            .where(Transaction.category_id.isnot(None))
            .group_by(
                Transaction.category_id,
                Category.name,
                Category.icon,
                Category.color,
            )
            .order_by(func.sum(Transaction.amount).desc())
        )
        rows = result.all()

        # Calculate total
        total = sum(row.amount for row in rows) if rows else Decimal(0)

        # Build category spending list
        categories = []
        for row in rows:
            percentage = (
                (row.amount / total * 100) if total > 0 else Decimal(0)
            )
            categories.append(
                CategorySpending(
                    category_id=row.category_id,
                    category_name=row.name,
                    category_icon=row.icon,
                    category_color=row.color,
                    amount=row.amount,
                    percentage=round(percentage, 2),
                    transaction_count=row.count,
                )
            )

        return CategoryBreakdownResponse(
            total=total,
            categories=categories,
        )
