"""Request schemas for the Result service."""

from __future__ import annotations

from core.api import MutationBody


class ResultSampleCreate(MutationBody):
    sampleId: int


class ResultSampleUpdate(MutationBody):
    pass


class ResultControlCreate(MutationBody):
    uploadResultSessionId: int


class ResultControlUpdate(MutationBody):
    pass
