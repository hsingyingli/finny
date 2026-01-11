from datetime import date
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction, TransactionTag, TransactionType
from app.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    """Repository for Transaction model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Transaction)

    async def get_by_user(
        self,
        user_id: UUID,
        transaction_type: TransactionType | None = None,
        category_id: UUID | None = None,
        account_id: UUID | None = None,
        tag_id: UUID | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        search_query: str | None = None,
    ) -> list[Transaction]:
        """Get all transactions for a user with optional filters."""
        query = select(Transaction).where(Transaction.user_id == user_id)

        if transaction_type:
            query = query.where(Transaction.type == transaction_type)
        if category_id:
            query = query.where(Transaction.category_id == category_id)
        if account_id:
            query = query.where(
                (Transaction.account_id == account_id)
                | (Transaction.to_account_id == account_id)
            )
        if start_date:
            query = query.where(Transaction.date >= start_date)
        if end_date:
            query = query.where(Transaction.date <= end_date)
        if search_query:
            query = query.where(Transaction.note.ilike(f"%{search_query}%"))

        query = query.order_by(Transaction.date.desc(), Transaction.created_at.desc())
        result = await self.session.execute(query)
        transactions = list(result.scalars().all())

        # Filter by tag if specified
        if tag_id:
            filtered = []
            for t in transactions:
                tag_ids = await self.get_tag_ids(t.id)
                if tag_id in tag_ids:
                    filtered.append(t)
            return filtered

        return transactions

    async def get_by_id_and_user(self, id: UUID, user_id: UUID) -> Transaction | None:
        """Get a transaction by ID and user."""
        result = await self.session.execute(
            select(Transaction).where(
                Transaction.id == id, Transaction.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_tag_ids(self, transaction_id: UUID) -> list[UUID]:
        """Get tag IDs for a transaction."""
        result = await self.session.execute(
            select(TransactionTag.tag_id).where(
                TransactionTag.transaction_id == transaction_id
            )
        )
        return [row[0] for row in result.all()]

    async def set_tags(self, transaction_id: UUID, tag_ids: list[UUID]) -> None:
        """Set tags for a transaction."""
        # Remove existing tags
        await self.session.execute(
            delete(TransactionTag).where(
                TransactionTag.transaction_id == transaction_id
            )
        )
        await self.session.flush()

        # Add new tags
        for tag_id in tag_ids:
            self.session.add(
                TransactionTag(transaction_id=transaction_id, tag_id=tag_id)
            )
        await self.session.flush()

    async def clear_tags(self, transaction_id: UUID) -> None:
        """Clear all tags from a transaction."""
        await self.session.execute(
            delete(TransactionTag).where(
                TransactionTag.transaction_id == transaction_id
            )
        )
        await self.session.flush()
