"""Request schemas for the Result service."""

from core.api import MutationBody


class ResultSampleCreate(MutationBody):
    sampleId: int


class ResultSampleUpdate(MutationBody):
    pass


class ResultControlCreate(MutationBody):
    uploadResultSessionId: int


class ResultControlUpdate(MutationBody):
    pass
