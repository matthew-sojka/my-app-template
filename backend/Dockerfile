# Slim official Python image: small, but has what most packages need.
FROM python:3.12-slim

# Copy the uv binary from its official image (pinned for reproducible builds).
COPY --from=ghcr.io/astral-sh/uv:0.11.33 /uv /uvx /bin/

WORKDIR /app

# UV_COMPILE_BYTECODE: precompile .py files so the container starts faster.
# UV_LINK_MODE=copy: avoids hardlink warnings inside Docker.
# PYTHONUNBUFFERED: send logs straight to stdout so `docker logs` shows them live.
# UV_PROJECT_ENVIRONMENT: build the virtualenv outside /app, so bind-mounting source
#   code over /app in local dev can't hide it.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv

# 1) Install dependencies only. This layer is cached until the lockfile changes.
#    --frozen: install exactly what uv.lock says (like `npm ci`).
#    --no-dev: skip pytest/ruff in the runtime image.
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev --no-install-project

# 2) Copy the application code (changes often, so it comes last).
COPY . .
RUN uv sync --frozen --no-dev

# Put the virtualenv's executables (uvicorn, alembic, etc.) on the PATH.
ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8000

# 0.0.0.0 makes the server reachable from outside the container.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
