# Finny - Coding Guidelines

## Tech Stack

- **Framework**: FastAPI (async)
- **Database**: PostgreSQL + pgvector (via SQLModel async)
- **Agent**: Agno
- **Validation**: Pydantic v2
- **Linting/Format**: Ruff (already configured in pyproject.toml)

## Architecture Layers

```
API (endpoints) → Service (business logic) → Repository (data access) → Model (ORM)
```

- **Endpoints**: HTTP handling only, no business logic
- **Services**: Orchestration, validation, business rules
- **Repositories**: Database queries, no business logic
- **Models**: SQLModel definitions (DB only, not for API response)

## Key Conventions

### Async Everywhere
All I/O operations must be async. Use `async def` for endpoints and `AsyncSession` for database.

### Dependency Injection
Use FastAPI's `Depends()` for services, database sessions, and settings. See `app/dependencies.py`.

### Model & Schema 分離
- **Model (SQLModel)**: 只負責 DB 定義，放 `app/models/`
- **Request/Response Schema**: 獨立定義，放 `<feature>/schemas.py`
- **Workflow schemas**: `app/agents/workflows/<name>/schemas.py`
- **Shared schemas**: `app/schemas/common.py` (Pagination, ErrorResponse)

### Error Handling
Raise custom exceptions from `app/exceptions.py`. Global handlers convert them to HTTP responses.

### Configuration
Use `pydantic-settings` in `app/config.py`. All secrets via environment variables.

## Commands

```bash
# Run development server
uv run uvicorn main:app --reload

# Run linter
uv run ruff check .

# Format code
uv run ruff format .

# Run tests
uv run pytest

# Database migration
uv run alembic upgrade head
```

## File References

For detailed patterns, see:
- Model example: `app/models/agent.py`
- Endpoint example: `app/api/v1/endpoints/agents/router.py`
- Service example: `app/services/agent_service.py`
- Repository example: `app/repositories/agent_repo.py`
