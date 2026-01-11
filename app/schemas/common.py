from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""

    data: T
    success: bool = True
    message: str | None = None


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str
    success: bool = False


class PaginationParams(BaseModel):
    """Pagination parameters."""

    skip: int = 0
    limit: int = 100


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response."""

    data: list[T]
    total: int
    skip: int
    limit: int
    success: bool = True


class EmptyResponse(BaseModel):
    """Empty response for delete/logout operations."""

    pass


class HealthStatus(BaseModel):
    """Health check response."""

    status: str = "healthy"


class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: str  # user_id
    exp: int  # expiration timestamp
    type: str = "access"  # "access" or "refresh"


class TokenData(BaseModel):
    """Data to encode in JWT token."""

    sub: str  # user_id
    type: str = "access"  # "access" or "refresh"
