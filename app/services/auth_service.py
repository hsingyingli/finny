from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth.schemas import AuthResponse, TokenResponse, UserResponse
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.exceptions import BadRequestError, UnauthorizedError
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.common import TokenData


class AuthService:
    """Service for authentication operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def register(self, email: str, password: str, name: str) -> AuthResponse:
        """Register a new user."""
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise BadRequestError("Email already registered")

        user = User(
            email=email,
            password_hash=hash_password(password),
            name=name,
        )
        user = await self.user_repo.create(user)

        token_data = TokenData(sub=str(user.id))
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)

        return AuthResponse(
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            ),
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def login(self, email: str, password: str) -> AuthResponse:
        """Login a user."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise UnauthorizedError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedError("User account is disabled")

        token_data = TokenData(sub=str(user.id))
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)

        return AuthResponse(
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            ),
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def logout(self) -> None:
        """Logout a user (placeholder - JWT is stateless)."""
        # In a stateless JWT system, logout is handled client-side
        # For token invalidation, you would need a token blacklist
        pass

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token."""
        payload = decode_refresh_token(refresh_token)
        if not payload:
            raise UnauthorizedError("Invalid or expired refresh token")

        # Verify user still exists and is active
        user = await self.user_repo.get_by_id(payload.sub)
        if not user:
            raise UnauthorizedError("User not found")
        if not user.is_active:
            raise UnauthorizedError("User account is disabled")

        # Generate new tokens
        token_data = TokenData(sub=str(user.id))
        new_access_token = create_access_token(data=token_data)
        new_refresh_token = create_refresh_token(data=token_data)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )
