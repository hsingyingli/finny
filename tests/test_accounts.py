from decimal import Decimal
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account, AccountType


@pytest.mark.asyncio
async def test_create_account(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
):
    """Test creating a new account."""
    response = await client.post(
        "/api/v1/accounts",
        headers=auth_headers,
        json={
            "name": "My Wallet",
            "type": "cash",
            "initial_balance": 1000.00,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "My Wallet"
    assert data["data"]["type"] == "cash"
    assert Decimal(data["data"]["balance"]) == Decimal("1000.00")
    assert Decimal(data["data"]["initial_balance"]) == Decimal("1000.00")


@pytest.mark.asyncio
async def test_get_accounts(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test getting all accounts."""
    # Create some accounts
    account1 = Account(
        user_id=UUID(test_user_id),
        name="Account 1",
        type=AccountType.CASH,
        balance=Decimal("100"),
        initial_balance=Decimal("100"),
    )
    account2 = Account(
        user_id=UUID(test_user_id),
        name="Account 2",
        type=AccountType.BANK,
        balance=Decimal("200"),
        initial_balance=Decimal("200"),
    )
    async_session.add_all([account1, account2])
    await async_session.commit()

    response = await client.get(
        "/api/v1/accounts",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 2


@pytest.mark.asyncio
async def test_get_accounts_include_archived(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test getting accounts including archived ones."""
    # Create accounts
    account1 = Account(
        user_id=UUID(test_user_id),
        name="Active Account",
        type=AccountType.CASH,
        is_archived=False,
    )
    account2 = Account(
        user_id=UUID(test_user_id),
        name="Archived Account",
        type=AccountType.BANK,
        is_archived=True,
    )
    async_session.add_all([account1, account2])
    await async_session.commit()

    # Without includeArchived
    response = await client.get(
        "/api/v1/accounts",
        headers=auth_headers,
    )
    assert len(response.json()["data"]) == 1

    # With includeArchived
    response = await client.get(
        "/api/v1/accounts?includeArchived=true",
        headers=auth_headers,
    )
    assert len(response.json()["data"]) == 2


@pytest.mark.asyncio
async def test_get_single_account(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test getting a single account."""
    account = Account(
        user_id=UUID(test_user_id),
        name="Single Account",
        type=AccountType.CASH,
    )
    async_session.add(account)
    await async_session.commit()
    await async_session.refresh(account)

    response = await client.get(
        f"/api/v1/accounts/{account.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Single Account"


@pytest.mark.asyncio
async def test_update_account(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test updating an account."""
    account = Account(
        user_id=UUID(test_user_id),
        name="Old Name",
        type=AccountType.CASH,
    )
    async_session.add(account)
    await async_session.commit()
    await async_session.refresh(account)

    response = await client.put(
        f"/api/v1/accounts/{account.id}",
        headers=auth_headers,
        json={"name": "New Name"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "New Name"


@pytest.mark.asyncio
async def test_archive_account(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test archiving an account (soft delete)."""
    account = Account(
        user_id=UUID(test_user_id),
        name="To Archive",
        type=AccountType.CASH,
    )
    async_session.add(account)
    await async_session.commit()
    await async_session.refresh(account)

    response = await client.delete(
        f"/api/v1/accounts/{account.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"]["is_archived"] is True


@pytest.mark.asyncio
async def test_adjust_balance(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test adjusting account balance."""
    account = Account(
        user_id=UUID(test_user_id),
        name="Balance Test",
        type=AccountType.CASH,
        balance=Decimal("100"),
    )
    async_session.add(account)
    await async_session.commit()
    await async_session.refresh(account)

    response = await client.patch(
        f"/api/v1/accounts/{account.id}/balance",
        headers=auth_headers,
        json={"delta": 50.00},
    )
    assert response.status_code == 200
    assert Decimal(response.json()["data"]["balance"]) == Decimal("150.00")


@pytest.mark.asyncio
async def test_set_default_account(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test setting an account as default."""
    account1 = Account(
        user_id=UUID(test_user_id),
        name="Account 1",
        type=AccountType.CASH,
        is_default=True,
    )
    account2 = Account(
        user_id=UUID(test_user_id),
        name="Account 2",
        type=AccountType.BANK,
        is_default=False,
    )
    async_session.add_all([account1, account2])
    await async_session.commit()
    await async_session.refresh(account2)

    response = await client.put(
        f"/api/v1/accounts/{account2.id}/default",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"]["is_default"] is True


@pytest.mark.asyncio
async def test_get_total_balance(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
):
    """Test getting total balance."""
    account1 = Account(
        user_id=UUID(test_user_id),
        name="Account 1",
        type=AccountType.CASH,
        balance=Decimal("100"),
    )
    account2 = Account(
        user_id=UUID(test_user_id),
        name="Account 2",
        type=AccountType.BANK,
        balance=Decimal("200"),
    )
    async_session.add_all([account1, account2])
    await async_session.commit()

    response = await client.get(
        "/api/v1/accounts/total-balance",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert Decimal(response.json()["data"]["total_balance"]) == Decimal("300.00")
