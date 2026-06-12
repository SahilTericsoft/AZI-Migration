"""Request schemas for the Sendout service."""

from __future__ import annotations

from core.api import MutationBody


class SendoutBatchCreate(MutationBody):
    sendoutLabId: int


class SendoutBatchUpdate(MutationBody):
    pass
