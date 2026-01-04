# Finny - Folder Structure

```
finny/
├── main.py                     # Application entry point
├── pyproject.toml              # Project configuration & dependencies
├── uv.lock                     # Dependency lock file
├── docker-compose.yml          # Docker orchestration
├── Dockerfile                  # Container build instructions
├── .env.example                # Environment variables template
│
├── app/                        # Main application package
│   ├── __init__.py
│   ├── config.py               # Settings & configuration (pydantic-settings)
│   ├── database.py             # Database connection & session management
│   ├── dependencies.py         # Shared FastAPI dependencies
│   ├── exceptions.py           # Custom exception classes
│   │
│   ├── api/                    # API layer
│   │   ├── __init__.py
│   │   ├── router.py           # Main API router (aggregates all routes)
│   │   └── v1/                 # API version 1
│   │       ├── __init__.py
│   │       ├── router.py       # v1 router
│   │       └── endpoints/      # Route handlers (feature-based)
│   │           ├── __init__.py
│   │           ├── health.py   # Simple endpoints can be single file
│   │           ├── agents/     # Feature module
│   │           │   ├── __init__.py
│   │           │   ├── router.py
│   │           │   └── schemas.py  # Request/Response schemas
│   │           └── conversations/
│   │               ├── __init__.py
│   │               ├── router.py
│   │               └── schemas.py
│   │
│   ├── models/                 # SQLModel definitions (DB only)
│   │   ├── __init__.py
│   │   ├── base.py             # Base model class
│   │   ├── agent.py
│   │   └── conversation.py
│   │
│   ├── schemas/                # Shared schemas only
│   │   ├── __init__.py
│   │   └── common.py           # Pagination, ErrorResponse, etc.
│   │
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── agent_service.py
│   │   └── conversation_service.py
│   │
│   ├── repositories/           # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py             # Base repository
│   │   └── agent_repo.py
│   │
│   ├── agents/                 # Agno agent definitions
│   │   ├── __init__.py
│   │   ├── base.py             # Base agent configuration
│   │   ├── tools/              # Custom tools for agents
│   │   │   ├── __init__.py
│   │   │   └── web_search.py
│   │   └── workflows/          # Agent workflows (co-located schemas)
│   │       ├── __init__.py
│   │       ├── chat/
│   │       │   ├── __init__.py
│   │       │   ├── workflow.py
│   │       │   └── schemas.py  # Workflow-specific schemas
│   │       └── summarize/
│   │           ├── __init__.py
│   │           ├── workflow.py
│   │           └── schemas.py
│   │
│   └── core/                   # Core utilities
│       ├── __init__.py
│       ├── security.py         # Auth, JWT, permissions
│       ├── logging.py          # Logging configuration
│       └── utils.py            # Shared utility functions
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── migrations/                 # Database migrations (Alembic)
│   ├── env.py
│   ├── alembic.ini
│   └── versions/
│
├── scripts/                    # Utility scripts
│   └── seed_db.py
│
└── docs/                       # Documentation
    ├── folder_structure.md
    ├── coding.md
    └── api.md
```

## Model & Schema 分離原則

| 類型 | 位置 | 說明 |
|------|------|------|
| DB Model | `app/models/` | SQLModel，只負責 DB 結構 |
| Request/Response | `app/api/v1/endpoints/<feature>/schemas.py` | Pydantic，API 契約 |
| Workflow I/O | `app/agents/workflows/<name>/schemas.py` | Agent 專用 |
| 共用 Schema | `app/schemas/common.py` | `PaginationParams`, `ErrorResponse` |

**原則：Model 與 Schema 分離，確保 DB 變動不影響 API 契約**

## Directory Responsibilities

| Directory | Purpose |
|-----------|---------|
| `app/api/` | HTTP layer - route definitions, request validation, response formatting |
| `app/models/` | SQLModel definitions (DB structure only) |
| `app/schemas/` | **Only** shared schemas used across multiple features |
| `app/services/` | Business logic, orchestration between repositories and external services |
| `app/repositories/` | Database queries, data access abstraction |
| `app/agents/` | Agno agent configurations, tools, and workflows |
| `app/core/` | Cross-cutting concerns (auth, logging, utilities) |

## Key Principles

1. **Co-location**: Keep related code together (schemas next to their endpoints/workflows)
2. **Separation of Concerns**: Each layer has a single responsibility
3. **Dependency Direction**: `api -> services -> repositories -> models`
4. **API Versioning**: New versions go in `app/api/v2/`, `app/api/v3/`, etc.
5. **Agent Isolation**: All agent-related code lives in `app/agents/`
