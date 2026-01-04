# Finny

記帳 APP 後端服務，具備 AI agent 功能。

## Tech Stack

- Python 3.12+, FastAPI (async), SQLModel, Agno
- PostgreSQL + pgvector
- Ruff (lint/format config in pyproject.toml)

## Architecture

```
API (endpoints) → Service (business logic) → Repository (data access) → Model (ORM)
```

- Model 與 Schema 分離：SQLModel 只負責 DB，Response Schema 獨立定義
- Agent 相關程式碼集中在 `app/agents/`

## Commands

```bash
# Dev server
uv run uvicorn main:app --reload

# Lint & format
uv run ruff check . && uv run ruff format .

# Test
uv run pytest

# Database migration
uv run alembic upgrade head
```

## Documentation

- `docs/folder_structure.md` - 專案結構與目錄職責
- `docs/coding.md` - Coding conventions 與架構細節
