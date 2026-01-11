from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.users.schemas import (
    UserPreferencesResponse,
    UserPreferencesUpdate,
    UserProfileResponse,
)
from app.exceptions import NotFoundError
from app.models.user import User
from app.repositories.user_repo import UserRepository


class UserService:
    """Service for user operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(session)

    def _to_profile_response(self, user: User) -> UserProfileResponse:
        return UserProfileResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            theme=user.theme,
            currency=user.currency,
            locale=user.locale,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def _to_preferences_response(self, user: User) -> UserPreferencesResponse:
        return UserPreferencesResponse(
            theme=user.theme,
            currency=user.currency,
            locale=user.locale,
        )

    async def get_by_id(self, user_id: UUID) -> UserProfileResponse:
        """Get user profile by ID."""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))
        return self._to_profile_response(user)

    async def get_preferences(self, user_id: UUID) -> UserPreferencesResponse:
        """Get user preferences."""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))
        return self._to_preferences_response(user)

    async def update_preferences(
        self,
        user_id: UUID,
        data: UserPreferencesUpdate,
    ) -> UserPreferencesResponse:
        """Update user preferences."""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)
        user.updated_at = datetime.now(UTC)

        await self.repo.update(user)
        return self._to_preferences_response(user)
