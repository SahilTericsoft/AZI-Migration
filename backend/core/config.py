"""Minimal app settings, read from environment / .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"  # development | production
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/azi_db"
    jwt_secret: str = "change-me"
    jwt_expires_minutes: int = 60
    instance_code: str = "AZI"  # prefix for generated internalUserId

    # ---- security ----
    # Comma-separated allowed CORS origins (empty = none allowed).
    cors_origins: str = ""
    # Comma-separated allowed Host headers ("*" = any; restrict in production).
    allowed_hosts: str = "*"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def allowed_host_list(self) -> list[str]:
        return [h.strip() for h in self.allowed_hosts.split(",") if h.strip()] or ["*"]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


settings = Settings()
