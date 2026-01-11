import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_jwt_middleware_no_token(client: AsyncClient):
    """Test that requests without token return 401."""
    response = await client.get("/api/v1/accounts")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_jwt_middleware_invalid_token(client: AsyncClient):
    """Test that requests with invalid token return 401."""
    response = await client.get(
        "/api/v1/accounts",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_api_response_format(client: AsyncClient, auth_headers: dict[str, str]):
    """Test that API responses have the correct format."""
    response = await client.get(
        "/api/v1/accounts",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "success" in data
    assert data["success"] is True


@pytest.mark.asyncio
async def test_validation_error_returns_422(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that validation errors return 422."""
    response = await client.post(
        "/api/v1/accounts",
        headers=auth_headers,
        json={},  # Missing required fields
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_not_found_returns_404(client: AsyncClient, auth_headers: dict[str, str]):
    """Test that non-existent resources return 404."""
    response = await client.get(
        "/api/v1/accounts/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"
