"""Request schemas for the Notification service."""

from pydantic import BaseModel

from core.api import MutationBody


class NotificationCreate(MutationBody):
    message: str
    toUserId: int


class NotificationEdit(MutationBody):
    pass


class NotificationListQuery(BaseModel):
    page: int | None = None
    limit: int | None = None
    toUserId: int | None = None
    isActive: bool | None = None
    search: str | None = None
