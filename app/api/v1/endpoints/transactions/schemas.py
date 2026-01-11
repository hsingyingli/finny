import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.models.transaction import TransactionType


class TransactionCreate(BaseModel):
    amount: Decimal
    type: TransactionType
    category_id: UUID | None = None
    account_id: UUID
    to_account_id: UUID | None = None
    date: datetime.date
    note: str | None = None
    tag_ids: list[UUID] | None = None


class TransactionUpdate(BaseModel):
    amount: Decimal | None = None
    type: TransactionType | None = None
    category_id: UUID | None = None
    account_id: UUID | None = None
    to_account_id: UUID | None = None
    date: datetime.date | None = None
    note: str | None = None
    tag_ids: list[UUID] | None = None


class TransactionFilter(BaseModel):
    type: TransactionType | None = None
    category_id: UUID | None = None
    account_id: UUID | None = None
    tag_id: UUID | None = None
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None
    search_query: str | None = None


class TransactionResponse(BaseModel):
    id: UUID
    amount: Decimal
    type: TransactionType
    category_id: UUID | None
    account_id: UUID
    to_account_id: UUID | None
    date: datetime.date
    note: str | None
    tag_ids: list[UUID]
    created_at: datetime.datetime
    updated_at: datetime.datetime
