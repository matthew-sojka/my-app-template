from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings, read from environment variables (or a .env file).

    Each field maps to an env var of the same name, case-insensitive:
    `database_url` is read from DATABASE_URL. Values are validated against
    the type hints, so a malformed setting fails fast at startup.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "App Template API"
    environment: str = "local"
    # Origins allowed to call the API from a browser (your Vite dev server by default).
    # In .env, list values are written as JSON: CORS_ORIGINS=["http://localhost:5173"]
    cors_origins: list[str] = ["http://localhost:5173"]
    # SQLAlchemy URL; the `+psycopg` part picks the driver (psycopg 3).
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/app"


settings = Settings()
