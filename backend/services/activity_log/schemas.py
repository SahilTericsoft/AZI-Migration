"""Request schemas for the Activity Log service."""

from __future__ import annotations

from pydantic import BaseModel

from core.api import MutationBody


class ActivityLogCreate(MutationBody):
    module: str


class ActivityLogBulkCreate(BaseModel):
    logs: list[dict]


class ActivityLogEdit(MutationBody):
    pass


class ActivityLogListQuery(BaseModel):
    page: int | None = None
    limit: int | None = None
    identityId: int | None = None
    userId: int | None = None
    module: str | None = None
    type: str | None = None
