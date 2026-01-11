import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.models.budget import BudgetPeriod


class BudgetCreate(BaseModel):
    category_id: UUID
    amount: Decimal
    period: BudgetPeriod
    start_date: datetime.date | None = None


class BudgetUpdate(BaseModel):
    amount: Decimal | None = None
    period: BudgetPeriod | None = None
    start_date: datetime.date | None = None


class BudgetResponse(BaseModel):
    id: UUID
    category_id: UUID
    amount: Decimal
    period: BudgetPeriod
    start_date: datetime.date
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
