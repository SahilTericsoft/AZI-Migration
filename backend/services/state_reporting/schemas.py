"""Request schemas for the State Reporting service."""

from __future__ import annotations

from core.api import MutationBody


class StateReportingCreate(MutationBody):
    pass


class StateReportingUpdate(MutationBody):
    pass


class StateReportingSessionCreate(MutationBody):
    stateReportingId: int


class StateReportingSessionUpdate(MutationBody):
    pass
