from uuid import UUID

from fastapi import APIRouter, Query

from app.api.v1.endpoints.accounts.schemas import (
    AccountBalanceUpdate,
    AccountCreate,
    AccountResponse,
    AccountUpdate,
    TotalBalanceResponse,
)
from app.dependencies import CurrentUserDep, SessionDep
from app.schemas.common import ApiResponse
from app.services.account_service import AccountService

router = APIRouter()


@router.get("/total-balance")
async def get_total_balance(
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[TotalBalanceResponse]:
    """Get total balance across all accounts."""
    service = AccountService(session)
    total = await service.get_total_balance(current_user_id)
    return ApiResponse(data=TotalBalanceResponse(total_balance=total))


@router.post("")
async def create_account(
    request: AccountCreate,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[AccountResponse]:
    """Create a new account."""
    service = AccountService(session)
    account = await service.create(current_user_id, request)
    return ApiResponse(data=account, message="Account created successfully")


@router.get("")
async def get_accounts(
    session: SessionDep,
    current_user_id: CurrentUserDep,
    include_archived: bool = Query(False, alias="includeArchived"),
) -> ApiResponse[list[AccountResponse]]:
    """Get all accounts."""
    service = AccountService(session)
    accounts = await service.get_all(current_user_id, include_archived)
    return ApiResponse(data=accounts)


@router.get("/{account_id}")
async def get_account(
    account_id: UUID,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[AccountResponse]:
    """Get a single account."""
    service = AccountService(session)
    account = await service.get_by_id(current_user_id, account_id)
    return ApiResponse(data=account)


@router.put("/{account_id}")
async def update_account(
    account_id: UUID,
    request: AccountUpdate,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[AccountResponse]:
    """Update an account."""
    service = AccountService(session)
    account = await service.update(current_user_id, account_id, request)
    return ApiResponse(data=account, message="Account updated successfully")


@router.delete("/{account_id}")
async def archive_account(
    account_id: UUID,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[AccountResponse]:
    """Archive an account (soft delete)."""
    service = AccountService(session)
    account = await service.archive(current_user_id, account_id)
    return ApiResponse(data=account, message="Account archived successfully")


@router.patch("/{account_id}/balance")
async def adjust_balance(
    account_id: UUID,
    request: AccountBalanceUpdate,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[AccountResponse]:
    """Adjust account balance."""
    service = AccountService(session)
    account = await service.adjust_balance(current_user_id, account_id, request.delta)
    return ApiResponse(data=account, message="Balance adjusted successfully")


@router.put("/{account_id}/default")
async def set_default_account(
    account_id: UUID,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[AccountResponse]:
    """Set an account as default."""
    service = AccountService(session)
    account = await service.set_default(current_user_id, account_id)
    return ApiResponse(data=account, message="Default account set successfully")
