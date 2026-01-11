from fastapi import APIRouter

from app.api.v1.endpoints.auth.schemas import (
    AuthResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.dependencies import CurrentUserDep, SessionDep
from app.schemas.common import ApiResponse, EmptyResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register")
async def register(
    request: RegisterRequest, session: SessionDep
) -> ApiResponse[AuthResponse]:
    """Register a new user."""
    service = AuthService(session)
    result = await service.register(
        email=request.email,
        password=request.password,
        name=request.name,
    )
    return ApiResponse(data=result, message="User registered successfully")


@router.post("/login")
async def login(
    request: LoginRequest, session: SessionDep
) -> ApiResponse[AuthResponse]:
    """Login a user."""
    service = AuthService(session)
    result = await service.login(
        email=request.email,
        password=request.password,
    )
    return ApiResponse(data=result, message="Login successful")


@router.post("/logout")
async def logout(
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ApiResponse[EmptyResponse]:
    """Logout the current user."""
    service = AuthService(session)
    await service.logout()
    return ApiResponse(data=EmptyResponse(), message="Logout successful")


@router.post("/refresh")
async def refresh_token(
    request: RefreshRequest, session: SessionDep
) -> ApiResponse[TokenResponse]:
    """Refresh access token using refresh token."""
    service = AuthService(session)
    result = await service.refresh_token(refresh_token=request.refresh_token)
    return ApiResponse(data=result, message="Token refreshed successfully")
