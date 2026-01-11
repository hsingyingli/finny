from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag
from app.repositories.base import BaseRepository


class TagRepository(BaseRepository[Tag]):
    """Repository for Tag model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Tag)

    async def get_by_user(self, user_id: UUID) -> list[Tag]:
        """Get all tags for a user, sorted by usage count descending."""
        result = await self.session.execute(
            select(Tag)
            .where(Tag.user_id == user_id)
            .order_by(Tag.usage_count.desc(), Tag.created_at)
        )
        return list(result.scalars().all())

    async def get_by_id_and_user(self, id: UUID, user_id: UUID) -> Tag | None:
        """Get a tag by ID and user."""
        result = await self.session.execute(
            select(Tag).where(Tag.id == id, Tag.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def search(self, user_id: UUID, query: str) -> list[Tag]:
        """Search tags by name."""
        result = await self.session.execute(
            select(Tag)
            .where(
                Tag.user_id == user_id,
                Tag.name.ilike(f"%{query}%"),
            )
            .order_by(Tag.usage_count.desc())
        )
        return list(result.scalars().all())

    async def get_by_ids(self, tag_ids: list[UUID], user_id: UUID) -> list[Tag]:
        """Get tags by IDs."""
        if not tag_ids:
            return []
        result = await self.session.execute(
            select(Tag).where(Tag.id.in_(tag_ids), Tag.user_id == user_id)
        )
        return list(result.scalars().all())
