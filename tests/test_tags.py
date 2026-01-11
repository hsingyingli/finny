from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag


@pytest.mark.asyncio
async def test_create_tag(
    client: AsyncClient,
    auth_headers: dict[str, str],
):
    """Test creating a new tag."""
    response = await client.post(
        "/api/v1/tags",
        headers=auth_headers,
        json={
            "name": "Groceries",
            "color": "#FF5733",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Groceries"
    assert data["data"]["usage_count"] == 0


@pytest.mark.asyncio
async def test_get_tags_sorted_by_usage(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test getting tags sorted by usage count."""
    tag1 = Tag(
        user_id=UUID(test_user_id),
        name="Low Usage",
        usage_count=1,
    )
    tag2 = Tag(
        user_id=UUID(test_user_id),
        name="High Usage",
        usage_count=10,
    )
    async_session.add_all([tag1, tag2])
    await async_session.commit()

    response = await client.get(
        "/api/v1/tags",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 2
    # Should be sorted by usage_count descending
    assert data[0]["name"] == "High Usage"
    assert data[1]["name"] == "Low Usage"


@pytest.mark.asyncio
async def test_get_single_tag(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test getting a single tag."""
    tag = Tag(
        user_id=UUID(test_user_id),
        name="Single Tag",
    )
    async_session.add(tag)
    await async_session.commit()
    await async_session.refresh(tag)

    response = await client.get(
        f"/api/v1/tags/{tag.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Single Tag"


@pytest.mark.asyncio
async def test_search_tags(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test searching tags by name."""
    tag1 = Tag(
        user_id=UUID(test_user_id),
        name="Groceries",
    )
    tag2 = Tag(
        user_id=UUID(test_user_id),
        name="Restaurant",
    )
    async_session.add_all([tag1, tag2])
    await async_session.commit()

    response = await client.get(
        "/api/v1/tags/search?query=groc",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["name"] == "Groceries"


@pytest.mark.asyncio
async def test_update_tag(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test updating a tag."""
    tag = Tag(
        user_id=UUID(test_user_id),
        name="Old Name",
    )
    async_session.add(tag)
    await async_session.commit()
    await async_session.refresh(tag)

    response = await client.put(
        f"/api/v1/tags/{tag.id}",
        headers=auth_headers,
        json={"name": "New Name"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_tag(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test deleting a tag."""
    tag = Tag(
        user_id=UUID(test_user_id),
        name="To Delete",
    )
    async_session.add(tag)
    await async_session.commit()
    await async_session.refresh(tag)

    response = await client.delete(
        f"/api/v1/tags/{tag.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
