from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.accounts.schemas import (
    AccountCreate,
    AccountResponse,
    AccountUpdate,
)
from app.exceptions import NotFoundError
from app.models.account import Account
from app.repositories.account_repo import AccountRepository


class AccountService:
    """Service for account operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = AccountRepository(session)

    def _to_response(self, account: Account) -> AccountResponse:
        return AccountResponse(
            id=account.id,
            name=account.name,
            type=account.type,
            balance=account.balance,
            initial_balance=account.initial_balance,
            icon=account.icon,
            color=account.color,
            is_default=account.is_default,
            is_archived=account.is_archived,
            order=account.order,
            created_at=account.created_at,
            updated_at=account.updated_at,
        )

    async def create(self, user_id: UUID, data: AccountCreate) -> AccountResponse:
        """Create a new account."""
        max_order = await self.repo.get_max_order(user_id)
        account = Account(
            user_id=user_id,
            name=data.name,
            type=data.type,
            balance=data.initial_balance,
            initial_balance=data.initial_balance,
            icon=data.icon,
            color=data.color,
            order=max_order + 1,
        )
        account = await self.repo.create(account)
        return self._to_response(account)

    async def get_all(
        self,
        user_id: UUID,
        include_archived: bool = False,
    ) -> list[AccountResponse]:
        """Get all accounts for a user."""
        accounts = await self.repo.get_by_user(user_id, include_archived)
        return [self._to_response(a) for a in accounts]

    async def get_by_id(self, user_id: UUID, account_id: UUID) -> AccountResponse:
        """Get a single account."""
        account = await self.repo.get_by_id_and_user(account_id, user_id)
        if not account:
            raise NotFoundError("Account", str(account_id))
        return self._to_response(account)

    async def update(
        self,
        user_id: UUID,
        account_id: UUID,
        data: AccountUpdate,
    ) -> AccountResponse:
        """Update an account."""
        account = await self.repo.get_by_id_and_user(account_id, user_id)
        if not account:
            raise NotFoundError("Account", str(account_id))

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(account, key, value)
        account.updated_at = datetime.now(UTC)

        account = await self.repo.update(account)
        return self._to_response(account)

    async def archive(self, user_id: UUID, account_id: UUID) -> AccountResponse:
        """Archive an account (soft delete)."""
        account = await self.repo.get_by_id_and_user(account_id, user_id)
        if not account:
            raise NotFoundError("Account", str(account_id))

        account.is_archived = True
        account.updated_at = datetime.now(UTC)
        account = await self.repo.update(account)
        return self._to_response(account)

    async def adjust_balance(
        self,
        user_id: UUID,
        account_id: UUID,
        delta: Decimal,
    ) -> AccountResponse:
        """Adjust account balance by delta."""
        account = await self.repo.get_by_id_and_user(account_id, user_id)
        if not account:
            raise NotFoundError("Account", str(account_id))

        account.balance += delta
        account.updated_at = datetime.now(UTC)
        account = await self.repo.update(account)
        return self._to_response(account)

    async def set_default(self, user_id: UUID, account_id: UUID) -> AccountResponse:
        """Set an account as default."""
        account = await self.repo.get_by_id_and_user(account_id, user_id)
        if not account:
            raise NotFoundError("Account", str(account_id))

        # Clear existing default
        await self.repo.clear_default(user_id)

        account.is_default = True
        account.updated_at = datetime.now(UTC)
        account = await self.repo.update(account)
        return self._to_response(account)

    async def get_total_balance(self, user_id: UUID) -> Decimal:
        """Get total balance across all accounts."""
        return await self.repo.get_total_balance(user_id)
