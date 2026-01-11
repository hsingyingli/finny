import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from app.api.v1.endpoints.transactions.schemas import (
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
)
from app.dependencies import CurrentUserDep, SessionDep
from app.models.transaction import TransactionType
from app.schemas.common import ApiResponse, EmptyResponse
from app.services.transaction_service import TransactionService

router = APIRouter()


@router.post("")
async def create_transaction(
    request: TransactionCreate,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[TransactionResponse]:
    """Create a new transaction."""
    service = TransactionService(session)
    transaction = await service.create(current_user_id, request)
    return ApiResponse(data=transaction, message="Transaction created successfully")


@router.get("")
async def get_transactions(
    session: SessionDep,
    current_user_id: CurrentUserDep,
    type: Annotated[TransactionType | None, Query()] = None,
    category_id: Annotated[UUID | None, Query(alias="categoryId")] = None,
    account_id: Annotated[UUID | None, Query(alias="accountId")] = None,
    tag_id: Annotated[UUID | None, Query(alias="tagId")] = None,
    start_date: Annotated[datetime.date | None, Query(alias="startDate")] = None,
    end_date: Annotated[datetime.date | None, Query(alias="endDate")] = None,
    search_query: Annotated[str | None, Query(alias="searchQuery")] = None,
) -> ApiResponse[list[TransactionResponse]]:
    """Get all transactions with optional filters."""
    service = TransactionService(session)
    transactions = await service.get_all(
        current_user_id,
        type,
        category_id,
        account_id,
        tag_id,
        start_date,
        end_date,
        search_query,
    )
    return ApiResponse(data=transactions)


@router.get("/{transaction_id}")
async def get_transaction(
    transaction_id: UUID,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[TransactionResponse]:
    """Get a single transaction."""
    service = TransactionService(session)
    transaction = await service.get_by_id(current_user_id, transaction_id)
    return ApiResponse(data=transaction)


@router.put("/{transaction_id}")
async def update_transaction(
    transaction_id: UUID,
    request: TransactionUpdate,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[TransactionResponse]:
    """Update a transaction."""
    service = TransactionService(session)
    transaction = await service.update(current_user_id, transaction_id, request)
    return ApiResponse(data=transaction, message="Transaction updated successfully")


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: UUID,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[EmptyResponse]:
    """Delete a transaction."""
    service = TransactionService(session)
    await service.delete(current_user_id, transaction_id)
    return ApiResponse(data=EmptyResponse(), message="Transaction deleted successfully")
