from fastapi import APIRouter

from app.api.v1.endpoints.users.schemas import (
    UserPreferencesResponse,
    UserPreferencesUpdate,
    UserProfileResponse,
)
from app.dependencies import CurrentUserDep, SessionDep
from app.schemas.common import ApiResponse
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me")
async def get_current_user(
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[UserProfileResponse]:
    """Get current user profile."""
    service = UserService(session)
    user = await service.get_by_id(current_user_id)
    return ApiResponse(data=user)


@router.get("/me/preferences")
async def get_preferences(
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[UserPreferencesResponse]:
    """Get current user preferences."""
    service = UserService(session)
    preferences = await service.get_preferences(current_user_id)
    return ApiResponse(data=preferences)


@router.put("/me/preferences")
async def update_preferences(
    request: UserPreferencesUpdate,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[UserPreferencesResponse]:
    """Update current user preferences."""
    service = UserService(session)
    preferences = await service.update_preferences(current_user_id, request)
    return ApiResponse(data=preferences, message="Preferences updated successfully")
