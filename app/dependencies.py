from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.core.security import decode_access_token
from app.database import get_session
from app.exceptions import UnauthorizedError


async def get_current_user_id(
    authorization: Annotated[str | None, Header()] = None,
) -> UUID:
    """Extract and validate user ID from JWT token."""
    if not authorization:
        raise UnauthorizedError("Authorization header missing")

    if not authorization.startswith("Bearer "):
        raise UnauthorizedError("Invalid authorization header format")

    token = authorization[7:]  # Remove "Bearer " prefix
    payload = decode_access_token(token)

    if not payload:
        raise UnauthorizedError("Invalid or expired token")

    return UUID(payload.sub)


# Type aliases for dependency injection
SessionDep = Annotated[AsyncSession, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
CurrentUserDep = Annotated[UUID, Depends(get_current_user_id)]
