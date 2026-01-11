from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.tags.schemas import TagCreate, TagResponse, TagUpdate
from app.exceptions import NotFoundError
from app.models.tag import Tag
from app.repositories.tag_repo import TagRepository


class TagService:
    """Service for tag operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = TagRepository(session)

    def _to_response(self, tag: Tag) -> TagResponse:
        return TagResponse(
            id=tag.id,
            name=tag.name,
            color=tag.color,
            usage_count=tag.usage_count,
            created_at=tag.created_at,
            updated_at=tag.updated_at,
        )

    async def create(self, user_id: UUID, data: TagCreate) -> TagResponse:
        """Create a new tag."""
        tag = Tag(
            user_id=user_id,
            name=data.name,
            color=data.color or "#6B7280",
        )
        tag = await self.repo.create(tag)
        return self._to_response(tag)

    async def get_all(self, user_id: UUID) -> list[TagResponse]:
        """Get all tags for a user."""
        tags = await self.repo.get_by_user(user_id)
        return [self._to_response(t) for t in tags]

    async def get_by_id(self, user_id: UUID, tag_id: UUID) -> TagResponse:
        """Get a single tag."""
        tag = await self.repo.get_by_id_and_user(tag_id, user_id)
        if not tag:
            raise NotFoundError("Tag", str(tag_id))
        return self._to_response(tag)

    async def search(self, user_id: UUID, query: str) -> list[TagResponse]:
        """Search tags by name."""
        tags = await self.repo.search(user_id, query)
        return [self._to_response(t) for t in tags]

    async def get_by_ids(self, user_id: UUID, tag_ids: list[UUID]) -> list[TagResponse]:
        """Get multiple tags by IDs."""
        tags = await self.repo.get_by_ids(tag_ids, user_id)
        return [self._to_response(t) for t in tags]

    async def update(
        self,
        user_id: UUID,
        tag_id: UUID,
        data: TagUpdate,
    ) -> TagResponse:
        """Update a tag."""
        tag = await self.repo.get_by_id_and_user(tag_id, user_id)
        if not tag:
            raise NotFoundError("Tag", str(tag_id))

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(tag, key, value)
        tag.updated_at = datetime.now(UTC)

        tag = await self.repo.update(tag)
        return self._to_response(tag)

    async def delete(self, user_id: UUID, tag_id: UUID) -> None:
        """Delete a tag."""
        tag = await self.repo.get_by_id_and_user(tag_id, user_id)
        if not tag:
            raise NotFoundError("Tag", str(tag_id))
        await self.repo.delete(tag)

    async def increment_usage(self, tag_ids: list[UUID], user_id: UUID) -> None:
        """Increment usage count for tags."""
        tags = await self.repo.get_by_ids(tag_ids, user_id)
        for tag in tags:
            tag.usage_count += 1
            tag.updated_at = datetime.now(UTC)
            await self.repo.update(tag)

    async def decrement_usage(self, tag_ids: list[UUID], user_id: UUID) -> None:
        """Decrement usage count for tags."""
        tags = await self.repo.get_by_ids(tag_ids, user_id)
        for tag in tags:
            if tag.usage_count > 0:
                tag.usage_count -= 1
                tag.updated_at = datetime.now(UTC)
                await self.repo.update(tag)
