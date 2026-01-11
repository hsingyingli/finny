import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repo import UserRepository


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient, async_session: AsyncSession):
    """Test successful user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "name": "Test User",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["user"]["email"] == "test@example.com"
    assert data["data"]["user"]["name"] == "Test User"
    assert "token" in data["data"]

    # Verify password is hashed in database
    repo = UserRepository(async_session)
    user = await repo.get_by_email("test@example.com")
    assert user is not None
    assert user.password_hash != "password123"


@pytest.mark.asyncio
async def test_register_duplicate_email(
    client: AsyncClient, async_session: AsyncSession
):
    """Test registration with duplicate email."""
    # Create first user
    user = User(
        email="duplicate@example.com",
        password_hash="hashed",
        name="First User",
    )
    async_session.add(user)
    await async_session.commit()

    # Try to register with same email
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
            "name": "Second User",
        },
    )
    assert response.status_code == 400
    assert response.json()["success"] is False


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, async_session: AsyncSession):
    """Test successful login."""
    # Register a user first
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "password123",
            "name": "Login User",
        },
    )

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["user"]["email"] == "login@example.com"
    assert "token" in data["data"]


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, async_session: AsyncSession):
    """Test login with wrong password."""
    # Register a user first
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrong@example.com",
            "password": "password123",
            "name": "Wrong User",
        },
    )

    # Try to login with wrong password
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, auth_headers: dict[str, str]):
    """Test logout."""
    response = await client.post(
        "/api/v1/auth/logout",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
