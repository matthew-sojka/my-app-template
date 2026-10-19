# CLAUDE.md

Context for Claude Code. Read this at the start of every session.

## What this project is

A **reusable full-stack application template**, not a specific app. The goal is a solid
foundation that can be cloned to start future projects on the same stack. Favor patterns
that generalize well over app-specific shortcuts.

The stack is the current plan and may change; keep layers loosely coupled so a piece can be
swapped later.

## Working with me

- I'm a senior engineer with a strong **frontend** background (React, TypeScript,
  Next.js). I'm **learning the backend, database, DevOps, and cloud parts as we go.**
- **Explain as you work.** When you install, configure, or introduce something on the
  backend/infra side, say what it is, why it's needed, and, where it helps, what the
  frontend/Node equivalent is (e.g. `uv.lock` ≈ `package-lock.json`).
- Skip explanations of frontend basics I already know.
- **Work iteratively.** Finish one phase (see roadmap) with something working and verified
  before starting the next. Prefer small, reviewable steps over large rewrites.
- Verify changes by actually running them (tests, lint, `docker compose up`, curl the
  endpoint) rather than assuming they work.
- When pinning dependency or image versions, prefer releases that are at least a couple of
  weeks old.

## Stack

| Layer    | Choice                                                          |
|----------|-----------------------------------------------------------------|
| Frontend | React + TypeScript (Vite), TanStack Query (server state)        |
| Backend  | Python 3.12, FastAPI, Uvicorn (ASGI server)                     |
| Config   | pydantic-settings (typed settings from env vars / `.env`)       |
| Database | Postgres 16, SQLAlchemy 2.x (ORM), psycopg 3 (driver), Alembic (migrations) |
| Tooling  | uv (deps/venv), Ruff (lint + format), pytest, httpx2 (test client); Vitest + Testing Library (frontend) |
| Local    | Docker + Docker Compose                                         |
| CI       | GitHub Actions (`.github/workflows/ci.yml`); CD planned        |
| Cloud    | Planned — AWS or Azure (not yet decided)                        |

## Roadmap

1. **Repo structure + local dev with Docker Compose** — backend done; frontend pending
2. **FastAPI + Postgres with SQLAlchemy and Alembic migrations** — done (example `items` resource)
3. React frontend wired to the API (typed client generated from OpenAPI, env config, CORS)
4. **Tests + CI (GitHub Actions)** — workflow written and verified locally; not yet run on GitHub
5. Production containers + cloud deploy (registry, managed Postgres, hosting)
6. CD, secrets management, infrastructure as code (Terraform)
7. Auth, observability, hardening

**Current status:** backend + Postgres verified under `docker compose up` (lint, tests,
`/api/health`, migrations apply on startup). `items` is a full example resource (model,
migration, schemas, CRUD routes, DB tests). The frontend calls `/api/health` via TanStack
Query (Vite proxies `/api` to the backend); typed client generation is still Phase 3.
CI runs three parallel jobs: backend (Ruff, migrations, pytest against a Postgres service),
frontend (ESLint, Vitest, build), and a backend Docker image build.

## Repo layout

```
.
├── CLAUDE.md
├── .github/workflows/ci.yml  # CI: backend, frontend, docker jobs
├── docker-compose.yml        # db (Postgres) + backend, with hot reload
├── backend/
│   ├── app/
│   │   ├── main.py           # create_app() factory, CORS, router registration
│   │   ├── core/config.py    # Settings (env vars)
│   │   ├── db/base.py        # SQLAlchemy Base (+ constraint naming convention)
│   │   ├── db/session.py     # engine, SessionLocal, get_db() dependency
│   │   ├── models/           # ORM models (DB shape); import each in models/__init__.py
│   │   ├── schemas/          # Pydantic request/response models (API shape)
│   │   └── api/routes/       # one module per resource (health.py, items.py)
│   ├── alembic/              # env.py (wired to Settings + Base) and versions/
│   ├── alembic.ini
│   ├── tests/                # conftest.py: `client`/`db_session` fixtures (rolled back per test)
│   ├── pyproject.toml        # deps + Ruff + pytest config
│   ├── uv.lock               # committed lockfile
│   ├── Dockerfile
│   └── .env.example
└── frontend/                 # Vite react-ts; src/api/ = fetch wrapper + query options
```

## Commands

Backend (run from `backend/`):

```bash
uv sync                                  # install deps incl. dev tools
uv run uvicorn app.main:app --reload     # dev server → http://localhost:8000/docs
uv run pytest                            # tests
uv run ruff check .                      # lint
uv run ruff format .                     # format
uv add <pkg> / uv add --dev <pkg>        # add dependencies
uv run alembic revision --autogenerate -m "msg"   # new migration (review it!)
uv run alembic upgrade head              # apply migrations
```

After changing dependencies, rebuild the image: `docker compose up --build`.

Frontend (run from `frontend/`; needs the backend on :8000):

```bash
npm run dev                              # http://localhost:5173, proxies /api → :8000
npm test                                 # Vitest, once (npm run test:watch to watch)
npm run lint && npm run build            # lint + type-check + production build
```

Full stack (run from repo root):

```bash
docker compose up --build                # Postgres + API with hot reload
docker compose down                      # stop (data persists in the pgdata volume)
```

## Conventions

- All API routes live under the `/api` prefix.
- Every endpoint declares a Pydantic `response_model`; the OpenAPI schema is the contract
  the frontend's TypeScript types will be generated from.
- Configuration comes **only** from environment variables via `Settings` — no hardcoded
  environment-specific values. The same image must run locally, in CI, and in the cloud.
- Never commit `.env`; keep `.env.example` up to date when adding settings.
- Schema changes go through Alembic migrations only; never `Base.metadata.create_all()`.
  Always review autogenerated migrations before applying.
- Endpoints get a DB session via `db: Annotated[Session, Depends(get_db)]`.
- `/api/health` is the single health check: it pings Postgres and returns 200 with
  `database: "ok"`, or 503 with the same body (`status: "degraded"`) if the DB is unreachable.
- Commit `uv.lock`. Keep Ruff and tests passing before considering a step done.
- Add a test alongside each new endpoint.
- Frontend calls relative `/api/...` URLs (never hardcode a host). Each endpoint gets a
  `queryOptions(...)` in `src/api/<resource>.ts`; components call `useQuery(thatOptions)`.
- **New resource = copy `items`:** `models/<name>.py` (+ import in `models/__init__.py`),
  `schemas/<name>.py` (`<Name>Create` / `<Name>Update` / `<Name>Read`), `api/routes/<name>.py`
  (registered in `main.py`), an autogenerated migration (reviewed), `tests/test_<name>.py`.
- DB tests use the `client` fixture: each test runs in a transaction that's rolled back, so
  nothing persists. They need Postgres running and skip otherwise, except in CI (`CI=true`),
  where an unreachable DB fails the run. Locally they use the dev database; CI uses its own
  throwaway `app_test` database.
- CI also fails if models have drifted from migrations (`alembic check`) or a migration
  can't be downgraded. Pin third-party GitHub Actions to a commit SHA with a version comment.
- Frontend component tests sit next to the component (`X.test.tsx`), render with
  `renderWithQueryClient` from `src/test/render.tsx`, and stub `fetch` with `vi.stubGlobal`.
- Rely on DB constraints for integrity (e.g. unique → catch `IntegrityError` → 409), not
  check-then-write in Python.
