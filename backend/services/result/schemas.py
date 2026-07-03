"""Request schemas for the Result service."""

from __future__ import annotations

from pydantic import BaseModel

from core.api import MutationBody


class ResultSampleCreate(MutationBody):
    sampleId: int


class ResultSampleUpdate(MutationBody):
    pass


class ResultControlCreate(MutationBody):
    uploadResultSessionId: int


class ResultControlUpdate(MutationBody):
    pass


# --- result sessions / review ---
class ResultSessionListQuery(BaseModel):
    page: int | None = None
    limit: int | None = None
    search: str | None = None
    statuses: list[str] | None = None


class WorklistByTestPanelIn(BaseModel):
    testId: int | None = None
    biomarkerId: int | None = None
    sampleType: str | None = None


class ManualTemplateIn(BaseModel):
    worklistId: int | None = None
    worklistid: int | None = None
    testId: int | None = None
    biomarkerId: int | None = None


class ManualSubmitIn(MutationBody):
    worklistId: int | None = None
    testId: int | None = None
    biomarkerId: int | None = None
    biomarkerDetails: list | None = None
    accessionIds: list | None = None
    results: dict | None = None


class SessionActionIn(MutationBody):
    pass
