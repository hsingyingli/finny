from fastapi import APIRouter

from app.schemas.common import ApiResponse, HealthStatus

router = APIRouter()


@router.get("/health")
async def health_check() -> ApiResponse[HealthStatus]:
    """Health check endpoint."""
    return ApiResponse(data=HealthStatus(), message="Service is running")
