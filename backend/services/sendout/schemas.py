"""Request schemas for the Sendout service."""

from core.api import MutationBody


class SendoutBatchCreate(MutationBody):
    sendoutLabId: int


class SendoutBatchUpdate(MutationBody):
    pass
