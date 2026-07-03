"""Minimal app settings, read from environment / .env."""

from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"  # development | production
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/azi_db"

    @field_validator("database_url")
    @classmethod
    def _normalize_db_url(cls, v: str) -> str:
        # Hosts like Fly.io / Heroku inject `postgres://...`, which SQLAlchemy 2.0
        # rejects. Coerce any postgres scheme to the psycopg2 driver URL.
        for prefix in ("postgres://", "postgresql://"):
            if v.startswith(prefix):
                return "postgresql+psycopg2://" + v[len(prefix) :]
        return v

    jwt_secret: str = "change-me"
    jwt_expires_minutes: int = 60
    instance_code: str = "AZI"  # prefix for generated internalUserId

    # ---- Azure Blob storage (lab attachments) ----
    # Connection string for the storage account that owns the attachment
    # container. Kept in the environment (.env / Fly secret); empty disables
    # uploads (the endpoint returns 503 until it's configured + deployed).
    azure_storage_connection_string: str = ""
    azure_lab_attachments_container: str = "lab-attachments"

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
