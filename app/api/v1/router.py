from fastapi import APIRouter

from app.api.v1.endpoints.accounts.router import router as accounts_router
from app.api.v1.endpoints.auth.router import router as auth_router
from app.api.v1.endpoints.budgets.router import router as budgets_router
from app.api.v1.endpoints.categories.router import router as categories_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.statistics.router import router as statistics_router
from app.api.v1.endpoints.tags.router import router as tags_router
from app.api.v1.endpoints.transactions.router import router as transactions_router
from app.api.v1.endpoints.users.router import router as users_router

router = APIRouter()

router.include_router(health_router, tags=["health"])
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(accounts_router, prefix="/accounts", tags=["accounts"])
router.include_router(categories_router, prefix="/categories", tags=["categories"])
router.include_router(tags_router, prefix="/tags", tags=["tags"])
router.include_router(budgets_router, prefix="/budgets", tags=["budgets"])
router.include_router(
    transactions_router, prefix="/transactions", tags=["transactions"]
)
router.include_router(statistics_router, prefix="/statistics", tags=["statistics"])
