# Backend (FastAPI)

## Local development (without Docker)
```bash
uv sync                      # create .venv and install everything (incl. dev tools)
cp .env.example .env         # optional local overrides
uv run uvicorn app.main:app --reload
```
- API: http://localhost:8000/api/health
- Interactive docs: http://localhost:8000/docs

## Common commands
```bash
uv run pytest                # tests
uv run ruff check .          # lint
uv run ruff format .         # format
uv add <package>             # add a runtime dependency
uv add --dev <package>       # add a dev-only dependency
```

## Database migrations (Alembic)
Postgres must be running (`docker compose up db` from the repo root). Under
`docker compose up`, the backend applies pending migrations on startup.
```bash
# 1. Add/change a model in app/models/ (and import its module in app/models/__init__.py)
uv run alembic revision --autogenerate -m "add items table"   # 2. generate a migration
#    -> review the file in alembic/versions/ before applying it!
uv run alembic upgrade head      # 3. apply all pending migrations
uv run alembic downgrade -1      # undo the last migration
uv run alembic current           # which revision the database is at
uv run alembic check             # fails if models and migrations have drifted
```
