from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, items
from app.core.config import settings


def create_app() -> FastAPI:
    """App factory: building the app in a function makes it easy to create
    fresh instances with different settings in tests."""
    app = FastAPI(title=settings.app_name, version="0.1.0")

    # CORS lets the React dev server (a different origin/port) call this API.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Every route lives under /api, which keeps a clean split from frontend
    # routes and simplifies reverse-proxy rules when you deploy.
    app.include_router(health.router, prefix="/api")
    app.include_router(items.router, prefix="/api")
    return app


app = create_app()
