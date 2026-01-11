from decimal import Decimal
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import Budget, BudgetPeriod
from app.models.category import Category, CategoryType


@pytest.mark.asyncio
async def test_create_budget(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test creating a new budget."""
    # Create a category first
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

    response = await client.post(
        "/api/v1/budgets",
        headers=auth_headers,
        json={
            "category_id": str(category.id),
            "amount": 500.00,
            "period": "monthly",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["is_active"] is True
    assert Decimal(data["data"]["amount"]) == Decimal("500.00")


@pytest.mark.asyncio
async def test_get_budgets(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test getting all active budgets."""
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

    budget1 = Budget(
        user_id=UUID(test_user_id),
        category_id=category.id,
        amount=Decimal("500"),
        period=BudgetPeriod.MONTHLY,
        is_active=True,
    )
    budget2 = Budget(
        user_id=UUID(test_user_id),
        category_id=category.id,
        amount=Decimal("100"),
        period=BudgetPeriod.WEEKLY,
        is_active=False,
    )
    async_session.add_all([budget1, budget2])
    await async_session.commit()

    response = await client.get(
        "/api/v1/budgets",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    # Only active budgets
    assert len(data) == 1
    assert data[0]["is_active"] is True


@pytest.mark.asyncio
async def test_get_single_budget(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test getting a single budget."""
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

    budget = Budget(
        user_id=UUID(test_user_id),
        category_id=category.id,
        amount=Decimal("500"),
        period=BudgetPeriod.MONTHLY,
    )
    async_session.add(budget)
    await async_session.commit()
    await async_session.refresh(budget)

    response = await client.get(
        f"/api/v1/budgets/{budget.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert Decimal(response.json()["data"]["amount"]) == Decimal("500.00")


@pytest.mark.asyncio
async def test_get_budget_by_category(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test getting budget by category."""
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

    budget = Budget(
        user_id=UUID(test_user_id),
        category_id=category.id,
        amount=Decimal("500"),
        period=BudgetPeriod.MONTHLY,
    )
    async_session.add(budget)
    await async_session.commit()

    response = await client.get(
        f"/api/v1/budgets/category/{category.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"]["category_id"] == str(category.id)


@pytest.mark.asyncio
async def test_update_budget(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test updating a budget."""
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

    budget = Budget(
        user_id=UUID(test_user_id),
        category_id=category.id,
        amount=Decimal("500"),
        period=BudgetPeriod.MONTHLY,
    )
    async_session.add(budget)
    await async_session.commit()
    await async_session.refresh(budget)

    response = await client.put(
        f"/api/v1/budgets/{budget.id}",
        headers=auth_headers,
        json={"amount": 600.00},
    )
    assert response.status_code == 200
    assert Decimal(response.json()["data"]["amount"]) == Decimal("600.00")


@pytest.mark.asyncio
async def test_deactivate_budget(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test deactivating a budget (soft delete)."""
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

    budget = Budget(
        user_id=UUID(test_user_id),
        category_id=category.id,
        amount=Decimal("500"),
        period=BudgetPeriod.MONTHLY,
        is_active=True,
    )
    async_session.add(budget)
    await async_session.commit()
    await async_session.refresh(budget)

    response = await client.delete(
        f"/api/v1/budgets/{budget.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"]["is_active"] is False
