from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category, CategoryType


@pytest.mark.asyncio
async def test_create_category(
    client: AsyncClient,
    auth_headers: dict[str, str],
):
    """Test creating a new category."""
    response = await client.post(
        "/api/v1/categories",
        headers=auth_headers,
        json={
            "name": "Food",
            "icon": "food",
            "color": "#FF5733",
            "type": "expense",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Food"
    assert data["data"]["type"] == "expense"


@pytest.mark.asyncio
async def test_get_categories(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test getting all categories."""
    cat1 = Category(
        user_id=UUID(test_user_id),
        name="Food",
        icon="food",
        color="#FF5733",
        type=CategoryType.EXPENSE,
    )
    cat2 = Category(
        user_id=UUID(test_user_id),
        name="Salary",
        icon="money",
        color="#33FF57",
        type=CategoryType.INCOME,
    )
    async_session.add_all([cat1, cat2])
    await async_session.commit()

    response = await client.get(
        "/api/v1/categories",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2


@pytest.mark.asyncio
async def test_get_categories_by_type_income(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test filtering categories by income type."""
    cat1 = Category(
        user_id=UUID(test_user_id),
        name="Food",
        icon="food",
        color="#FF5733",
        type=CategoryType.EXPENSE,
    )
    cat2 = Category(
        user_id=UUID(test_user_id),
        name="Salary",
        icon="money",
        color="#33FF57",
        type=CategoryType.INCOME,
    )
    async_session.add_all([cat1, cat2])
    await async_session.commit()

    response = await client.get(
        "/api/v1/categories?type=income",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["type"] == "income"


@pytest.mark.asyncio
async def test_get_categories_by_type_expense(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test filtering categories by expense type."""
    cat1 = Category(
        user_id=UUID(test_user_id),
        name="Food",
        icon="food",
        color="#FF5733",
        type=CategoryType.EXPENSE,
    )
    cat2 = Category(
        user_id=UUID(test_user_id),
        name="Salary",
        icon="money",
        color="#33FF57",
        type=CategoryType.INCOME,
    )
    async_session.add_all([cat1, cat2])
    await async_session.commit()

    response = await client.get(
        "/api/v1/categories?type=expense",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["type"] == "expense"


@pytest.mark.asyncio
async def test_get_single_category(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test getting a single category."""
    category = Category(
        user_id=UUID(test_user_id),
        name="Food",
        icon="food",
        color="#FF5733",
        type=CategoryType.EXPENSE,
    )
    async_session.add(category)
    await async_session.commit()
    await async_session.refresh(category)

    response = await client.get(
        f"/api/v1/categories/{category.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Food"


@pytest.mark.asyncio
async def test_update_category(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test updating a category."""
    category = Category(
        user_id=UUID(test_user_id),
        name="Old Name",
        icon="old",
        color="#000000",
        type=CategoryType.EXPENSE,
    )
    async_session.add(category)
    await async_session.commit()
    await async_session.refresh(category)

    response = await client.put(
        f"/api/v1/categories/{category.id}",
        headers=auth_headers,
        json={"name": "New Name"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_category(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test deleting a custom category."""
    category = Category(
        user_id=UUID(test_user_id),
        name="Custom",
        icon="custom",
        color="#FF5733",
        type=CategoryType.EXPENSE,
        is_default=False,
    )
    async_session.add(category)
    await async_session.commit()
    await async_session.refresh(category)

    response = await client.delete(
        f"/api/v1/categories/{category.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_default_category_fails(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test that default categories cannot be deleted."""
    category = Category(
        user_id=UUID(test_user_id),
        name="Default",
        icon="default",
        color="#FF5733",
        type=CategoryType.EXPENSE,
        is_default=True,
    )
    async_session.add(category)
    await async_session.commit()
    await async_session.refresh(category)

    response = await client.delete(
        f"/api/v1/categories/{category.id}",
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_reorder_categories(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test reordering categories."""
    cat1 = Category(
        user_id=UUID(test_user_id),
        name="Cat 1",
        icon="1",
        color="#111111",
        type=CategoryType.EXPENSE,
        order=0,
    )
    cat2 = Category(
        user_id=UUID(test_user_id),
        name="Cat 2",
        icon="2",
        color="#222222",
        type=CategoryType.EXPENSE,
        order=1,
    )
    async_session.add_all([cat1, cat2])
    await async_session.commit()
    await async_session.refresh(cat1)
    await async_session.refresh(cat2)

    response = await client.put(
        "/api/v1/categories/reorder",
        headers=auth_headers,
        json={
            "type": "expense",
            "ordered_ids": [str(cat2.id), str(cat1.id)],
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    # After reorder, cat2 should be first (order=0)
    assert data[0]["id"] == str(cat2.id)
    assert data[0]["order"] == 0
