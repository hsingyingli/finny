from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.repositories.base import BaseRepository


class AccountRepository(BaseRepository[Account]):
    """Repository for Account model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Account)

    async def get_by_user(
        self,
        user_id: UUID,
        include_archived: bool = False,
    ) -> list[Account]:
        """Get all accounts for a user."""
        query = select(Account).where(Account.user_id == user_id)
        if not include_archived:
            query = query.where(Account.is_archived == False)  # noqa: E712
        query = query.order_by(Account.order, Account.created_at)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id_and_user(self, id: UUID, user_id: UUID) -> Account | None:
        """Get an account by ID and user."""
        result = await self.session.execute(
            select(Account).where(Account.id == id, Account.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_total_balance(self, user_id: UUID) -> Decimal:
        """Get total balance across all non-archived accounts."""
        result = await self.session.execute(
            select(func.coalesce(func.sum(Account.balance), Decimal("0"))).where(
                Account.user_id == user_id,
                Account.is_archived == False,  # noqa: E712
            )
        )
        return result.scalar_one() or Decimal("0")

    async def clear_default(self, user_id: UUID) -> None:
        """Clear default flag for all accounts of a user."""
        await self.session.execute(
            update(Account).where(Account.user_id == user_id).values(is_default=False)
        )

    async def get_max_order(self, user_id: UUID) -> int:
        """Get the maximum order value for a user's accounts."""
        result = await self.session.execute(
            select(func.coalesce(func.max(Account.order), -1)).where(
                Account.user_id == user_id
            )
        )
        return result.scalar_one() or -1
