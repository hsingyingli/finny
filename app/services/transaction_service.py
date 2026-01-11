from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.transactions.schemas import (
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
)
from app.exceptions import BadRequestError, NotFoundError
from app.models.transaction import Transaction, TransactionType
from app.repositories.account_repo import AccountRepository
from app.repositories.tag_repo import TagRepository
from app.repositories.transaction_repo import TransactionRepository


class TransactionService:
    """Service for transaction operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = TransactionRepository(session)
        self.account_repo = AccountRepository(session)
        self.tag_repo = TagRepository(session)

    async def _to_response(self, transaction: Transaction) -> TransactionResponse:
        tag_ids = await self.repo.get_tag_ids(transaction.id)
        return TransactionResponse(
            id=transaction.id,
            amount=transaction.amount,
            type=transaction.type,
            category_id=transaction.category_id,
            account_id=transaction.account_id,
            to_account_id=transaction.to_account_id,
            date=transaction.date,
            note=transaction.note,
            tag_ids=tag_ids,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at,
        )

    async def _apply_balance_change(
        self,
        user_id: UUID,
        account_id: UUID,
        amount: Decimal,
        transaction_type: TransactionType,
        to_account_id: UUID | None = None,
        reverse: bool = False,
    ) -> None:
        """Apply balance change to account(s)."""
        account = await self.account_repo.get_by_id_and_user(account_id, user_id)
        if not account:
            raise NotFoundError("Account", str(account_id))

        multiplier = Decimal("-1") if reverse else Decimal("1")

        if transaction_type == TransactionType.EXPENSE:
            account.balance -= amount * multiplier
        elif transaction_type == TransactionType.INCOME:
            account.balance += amount * multiplier
        elif transaction_type == TransactionType.TRANSFER:
            if not to_account_id:
                raise BadRequestError("Transfer requires to_account_id")
            to_account = await self.account_repo.get_by_id_and_user(
                to_account_id, user_id
            )
            if not to_account:
                raise NotFoundError("To Account", str(to_account_id))
            account.balance -= amount * multiplier
            to_account.balance += amount * multiplier
            to_account.updated_at = datetime.now(UTC)
            await self.account_repo.update(to_account)

        account.updated_at = datetime.now(UTC)
        await self.account_repo.update(account)

    async def create(
        self, user_id: UUID, data: TransactionCreate
    ) -> TransactionResponse:
        """Create a new transaction."""
        # Validate transfer requirements
        if data.type == TransactionType.TRANSFER and not data.to_account_id:
            raise BadRequestError("Transfer requires to_account_id")

        transaction = Transaction(
            user_id=user_id,
            amount=data.amount,
            type=data.type,
            category_id=data.category_id,
            account_id=data.account_id,
            to_account_id=data.to_account_id,
            date=data.date,
            note=data.note,
        )
        transaction = await self.repo.create(transaction)

        # Set tags and update usage count
        if data.tag_ids:
            await self.repo.set_tags(transaction.id, data.tag_ids)
            # Increment tag usage count
            tags = await self.tag_repo.get_by_ids(data.tag_ids, user_id)
            for tag in tags:
                tag.usage_count += 1
                tag.updated_at = datetime.now(UTC)
                await self.tag_repo.update(tag)

        # Apply balance change
        await self._apply_balance_change(
            user_id,
            data.account_id,
            data.amount,
            data.type,
            data.to_account_id,
        )

        return await self._to_response(transaction)

    async def get_all(
        self,
        user_id: UUID,
        transaction_type: TransactionType | None = None,
        category_id: UUID | None = None,
        account_id: UUID | None = None,
        tag_id: UUID | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        search_query: str | None = None,
    ) -> list[TransactionResponse]:
        """Get all transactions for a user with optional filters."""
        transactions = await self.repo.get_by_user(
            user_id,
            transaction_type,
            category_id,
            account_id,
            tag_id,
            start_date,
            end_date,
            search_query,
        )
        return [await self._to_response(t) for t in transactions]

    async def get_by_id(
        self, user_id: UUID, transaction_id: UUID
    ) -> TransactionResponse:
        """Get a single transaction."""
        transaction = await self.repo.get_by_id_and_user(transaction_id, user_id)
        if not transaction:
            raise NotFoundError("Transaction", str(transaction_id))
        return await self._to_response(transaction)

    async def update(
        self,
        user_id: UUID,
        transaction_id: UUID,
        data: TransactionUpdate,
    ) -> TransactionResponse:
        """Update a transaction."""
        transaction = await self.repo.get_by_id_and_user(transaction_id, user_id)
        if not transaction:
            raise NotFoundError("Transaction", str(transaction_id))

        # Reverse the old balance change
        await self._apply_balance_change(
            user_id,
            transaction.account_id,
            transaction.amount,
            transaction.type,
            transaction.to_account_id,
            reverse=True,
        )

        # Handle tag changes
        old_tag_ids = await self.repo.get_tag_ids(transaction_id)
        new_tag_ids = data.tag_ids

        if new_tag_ids is not None:
            # Decrement old tags
            old_tags = await self.tag_repo.get_by_ids(old_tag_ids, user_id)
            for tag in old_tags:
                if tag.usage_count > 0:
                    tag.usage_count -= 1
                    tag.updated_at = datetime.now(UTC)
                    await self.tag_repo.update(tag)

            # Set new tags
            await self.repo.set_tags(transaction_id, new_tag_ids)

            # Increment new tags
            new_tags = await self.tag_repo.get_by_ids(new_tag_ids, user_id)
            for tag in new_tags:
                tag.usage_count += 1
                tag.updated_at = datetime.now(UTC)
                await self.tag_repo.update(tag)

        # Update transaction fields
        update_data = data.model_dump(exclude_unset=True, exclude={"tag_ids"})
        for key, value in update_data.items():
            setattr(transaction, key, value)
        transaction.updated_at = datetime.now(UTC)

        transaction = await self.repo.update(transaction)

        # Apply the new balance change
        await self._apply_balance_change(
            user_id,
            transaction.account_id,
            transaction.amount,
            transaction.type,
            transaction.to_account_id,
        )

        return await self._to_response(transaction)

    async def delete(self, user_id: UUID, transaction_id: UUID) -> None:
        """Delete a transaction."""
        transaction = await self.repo.get_by_id_and_user(transaction_id, user_id)
        if not transaction:
            raise NotFoundError("Transaction", str(transaction_id))

        # Reverse the balance change
        await self._apply_balance_change(
            user_id,
            transaction.account_id,
            transaction.amount,
            transaction.type,
            transaction.to_account_id,
            reverse=True,
        )

        # Decrement tag usage
        tag_ids = await self.repo.get_tag_ids(transaction_id)
        if tag_ids:
            tags = await self.tag_repo.get_by_ids(tag_ids, user_id)
            for tag in tags:
                if tag.usage_count > 0:
                    tag.usage_count -= 1
                    tag.updated_at = datetime.now(UTC)
                    await self.tag_repo.update(tag)

        # Clear tags and delete transaction
        await self.repo.clear_tags(transaction_id)
        await self.repo.delete(transaction)
