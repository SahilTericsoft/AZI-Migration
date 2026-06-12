"""Request schemas for the Lab Operations service."""

from __future__ import annotations

from core.api import MutationBody


class DepartmentCreate(MutationBody):
    name: str


class DepartmentUpdate(MutationBody):
    pass


class InstrumentCreate(MutationBody):
    instrument: str


class InstrumentUpdate(MutationBody):
    pass


class SopCreate(MutationBody):
    sop_name: str


class SopUpdate(MutationBody):
    pass


class ValidationCreate(MutationBody):
    name_of_document: str


class ValidationUpdate(MutationBody):
    pass


class LabSessionCreate(MutationBody):
    pass


class LabSessionUpdate(MutationBody):
    pass
