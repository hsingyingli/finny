from datetime import date
from decimal import Decimal
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account, AccountType
from app.models.category import Category, CategoryType
from app.models.tag import Tag
from app.models.transaction import Transaction, TransactionType


@pytest.fixture
async def setup_data(async_session: AsyncSession, test_user_id: str):
    """Set up test data."""
    account = Account(
        user_id=UUID(test_user_id),
        name="Main Account",
        type=AccountType.CASH,
        balance=Decimal("1000"),
    )
    account2 = Account(
        user_id=UUID(test_user_id),
        name="Savings",
        type=AccountType.BANK,
        balance=Decimal("5000"),
    )
    category = Category(
        user_id=UUID(test_user_id),
        name="Food",
        icon="food",
        color="#FF5733",
        type=CategoryType.EXPENSE,
    )
    income_category = Category(
        user_id=UUID(test_user_id),
        name="Salary",
        icon="money",
        color="#33FF57",
        type=CategoryType.INCOME,
    )
    tag = Tag(
        user_id=UUID(test_user_id),
        name="Daily",
        usage_count=0,
    )
    async_session.add_all([account, account2, category, income_category, tag])
    await async_session.commit()
    await async_session.refresh(account)
    await async_session.refresh(account2)
    await async_session.refresh(category)
    await async_session.refresh(income_category)
    await async_session.refresh(tag)
    return {
        "account": account,
        "account2": account2,
        "category": category,
        "income_category": income_category,
        "tag": tag,
    }


@pytest.mark.asyncio
async def test_create_expense_transaction(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    setup_data,
):
    """Test creating an expense transaction."""
    data = setup_data
    response = await client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={
            "amount": 50.00,
            "type": "expense",
            "category_id": str(data["category"].id),
            "account_id": str(data["account"].id),
            "date": str(date.today()),
            "note": "Lunch",
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["data"]["type"] == "expense"

    # Check account balance decreased
    await async_session.refresh(data["account"])
    assert data["account"].balance == Decimal("950")


@pytest.mark.asyncio
async def test_create_income_transaction(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    setup_data,
):
    """Test creating an income transaction."""
    data = setup_data
    response = await client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={
            "amount": 1000.00,
            "type": "income",
            "category_id": str(data["income_category"].id),
            "account_id": str(data["account"].id),
            "date": str(date.today()),
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert result["data"]["type"] == "income"

    # Check account balance increased
    await async_session.refresh(data["account"])
    assert data["account"].balance == Decimal("2000")


@pytest.mark.asyncio
async def test_create_transfer_transaction(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    setup_data,
):
    """Test creating a transfer transaction."""
    data = setup_data
    response = await client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={
            "amount": 500.00,
            "type": "transfer",
            "account_id": str(data["account"].id),
            "to_account_id": str(data["account2"].id),
            "date": str(date.today()),
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert result["data"]["type"] == "transfer"

    # Check balances
    await async_session.refresh(data["account"])
    await async_session.refresh(data["account2"])
    assert data["account"].balance == Decimal("500")
    assert data["account2"].balance == Decimal("5500")


@pytest.mark.asyncio
async def test_create_transaction_with_tags(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    setup_data,
):
    """Test creating a transaction with tags increases usage count."""
    data = setup_data
    response = await client.post(
        "/api/v1/transactions",
        headers=auth_headers,
        json={
            "amount": 50.00,
            "type": "expense",
            "category_id": str(data["category"].id),
            "account_id": str(data["account"].id),
            "date": str(date.today()),
            "tag_ids": [str(data["tag"].id)],
        },
    )
    assert response.status_code == 200

    # Check tag usage increased
    await async_session.refresh(data["tag"])
    assert data["tag"].usage_count == 1


@pytest.mark.asyncio
async def test_get_transactions(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
    setup_data,
):
    """Test getting all transactions."""
    data = setup_data
    tx = Transaction(
        user_id=UUID(test_user_id),
        amount=Decimal("100"),
        type=TransactionType.EXPENSE,
        category_id=data["category"].id,
        account_id=data["account"].id,
        date=date.today(),
    )
    async_session.add(tx)
    await async_session.commit()

    response = await client.get(
        "/api/v1/transactions",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1


@pytest.mark.asyncio
async def test_filter_transactions_by_type(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
    setup_data,
):
    """Test filtering transactions by type."""
    data = setup_data
    tx1 = Transaction(
        user_id=UUID(test_user_id),
        amount=Decimal("100"),
        type=TransactionType.EXPENSE,
        category_id=data["category"].id,
        account_id=data["account"].id,
        date=date.today(),
    )
    tx2 = Transaction(
        user_id=UUID(test_user_id),
        amount=Decimal("1000"),
        type=TransactionType.INCOME,
        category_id=data["income_category"].id,
        account_id=data["account"].id,
        date=date.today(),
    )
    async_session.add_all([tx1, tx2])
    await async_session.commit()

    response = await client.get(
        "/api/v1/transactions?type=expense",
        headers=auth_headers,
    )
    assert response.status_code == 200
    result = response.json()["data"]
    assert len(result) == 1
    assert result[0]["type"] == "expense"


@pytest.mark.asyncio
async def test_filter_transactions_by_category(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
    setup_data,
):
    """Test filtering transactions by category."""
    data = setup_data
    tx = Transaction(
        user_id=UUID(test_user_id),
        amount=Decimal("100"),
        type=TransactionType.EXPENSE,
        category_id=data["category"].id,
        account_id=data["account"].id,
        date=date.today(),
    )
    async_session.add(tx)
    await async_session.commit()

    response = await client.get(
        f"/api/v1/transactions?categoryId={data['category'].id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1


@pytest.mark.asyncio
async def test_filter_transactions_by_account(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
    setup_data,
):
    """Test filtering transactions by account."""
    data = setup_data
    tx = Transaction(
        user_id=UUID(test_user_id),
        amount=Decimal("100"),
        type=TransactionType.EXPENSE,
        category_id=data["category"].id,
        account_id=data["account"].id,
        date=date.today(),
    )
    async_session.add(tx)
    await async_session.commit()

    response = await client.get(
        f"/api/v1/transactions?accountId={data['account'].id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1


@pytest.mark.asyncio
async def test_filter_transactions_by_date_range(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
    setup_data,
):
    """Test filtering transactions by date range."""
    data = setup_data
    tx = Transaction(
        user_id=UUID(test_user_id),
        amount=Decimal("100"),
        type=TransactionType.EXPENSE,
        category_id=data["category"].id,
        account_id=data["account"].id,
        date=date.today(),
    )
    async_session.add(tx)
    await async_session.commit()

    today = date.today()
    response = await client.get(
        f"/api/v1/transactions?startDate={today}&endDate={today}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1


@pytest.mark.asyncio
async def test_search_transactions_by_note(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
    setup_data,
):
    """Test searching transactions by note."""
    data = setup_data
    tx = Transaction(
        user_id=UUID(test_user_id),
        amount=Decimal("100"),
        type=TransactionType.EXPENSE,
        category_id=data["category"].id,
        account_id=data["account"].id,
        date=date.today(),
        note="Lunch at restaurant",
    )
    async_session.add(tx)
    await async_session.commit()

    response = await client.get(
        "/api/v1/transactions?searchQuery=restaurant",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1


@pytest.mark.asyncio
async def test_get_single_transaction(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
    setup_data,
):
    """Test getting a single transaction."""
    data = setup_data
    tx = Transaction(
        user_id=UUID(test_user_id),
        amount=Decimal("100"),
        type=TransactionType.EXPENSE,
        category_id=data["category"].id,
        account_id=data["account"].id,
        date=date.today(),
    )
    async_session.add(tx)
    await async_session.commit()
    await async_session.refresh(tx)

    response = await client.get(
        f"/api/v1/transactions/{tx.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert Decimal(response.json()["data"]["amount"]) == Decimal("100.00")


@pytest.mark.asyncio
async def test_update_transaction(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
    setup_data,
):
    """Test updating a transaction."""
    data = setup_data
    tx = Transaction(
        user_id=UUID(test_user_id),
        amount=Decimal("100"),
        type=TransactionType.EXPENSE,
        category_id=data["category"].id,
        account_id=data["account"].id,
        date=date.today(),
    )
    async_session.add(tx)
    await async_session.commit()
    await async_session.refresh(tx)

    # Account starts at 1000, tx deducted 100 (balance=900 after applying)
    # We need to setup initial state properly
    data["account"].balance = Decimal("900")
    await async_session.commit()

    response = await client.put(
        f"/api/v1/transactions/{tx.id}",
        headers=auth_headers,
        json={"amount": 150.00},
    )
    assert response.status_code == 200
    assert Decimal(response.json()["data"]["amount"]) == Decimal("150.00")

    # Balance should be adjusted: 900 + 100 (reverse old) - 150 (apply new) = 850
    await async_session.refresh(data["account"])
    assert data["account"].balance == Decimal("850")


@pytest.mark.asyncio
async def test_delete_transaction(
    client: AsyncClient,
    async_session: AsyncSession,
    auth_headers: dict[str, str],
    test_user_id: str,
    setup_data,
):
    """Test deleting a transaction."""
    data = setup_data
    tx = Transaction(
        user_id=UUID(test_user_id),
        amount=Decimal("100"),
        type=TransactionType.EXPENSE,
        category_id=data["category"].id,
        account_id=data["account"].id,
        date=date.today(),
    )
    async_session.add(tx)
    await async_session.commit()
    await async_session.refresh(tx)

    # Set account balance as if tx was already applied
    data["account"].balance = Decimal("900")
    await async_session.commit()

    response = await client.delete(
        f"/api/v1/transactions/{tx.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200

    # Balance should be restored: 900 + 100 = 1000
    await async_session.refresh(data["account"])
    assert data["account"].balance == Decimal("1000")
