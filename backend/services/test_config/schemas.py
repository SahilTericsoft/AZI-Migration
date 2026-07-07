"""Request schemas for the Test Configuration service.

Mirrors the legacy GkPanelService request bodies: rich list filters, view by id
with attribute projection, code-duplicate checks.
"""

from __future__ import annotations

from pydantic import BaseModel

from core.api import MutationBody


# ---- shared query bodies (ported from the legacy *List / *ListLite payloads) --
class CatalogListQuery(BaseModel):
    page: int | None = None
    limit: int | None = None
    search: str | None = None
    createdByIds: list[int] | None = None
    statuses: list[str] | None = None  # active / inactive / draft / completed
    sampleTypes: list[str] | None = None  # filter by sampleType (stored lowercase)
    startDate: str | None = None
    endDate: str | None = None
    sort: dict[str, str] | None = None  # {field: "ASC"|"DESC"}


class ListLiteQuery(BaseModel):
    ids: list[int] | None = None
    search: str | None = None
    isActive: bool | None = None
    appliedAttributes: list[str] | None = None


class CheckCodeIn(BaseModel):
    code: str


# ---- create / edit bodies (required fields per the legacy validators) ---------
class PanelCreate(MutationBody):
    name: str
    code: str


class PanelEdit(MutationBody):
    pass


class TestCreate(MutationBody):
    name: str
    code: str
    sampleType: str


class TestEdit(MutationBody):
    pass


class BiomarkerCreate(MutationBody):
    name: str
    code: str


class BiomarkerEdit(MutationBody):
    pass


class CptCodeCreate(MutationBody):
    cptCode: str


class CptCodeEdit(MutationBody):
    pass


class IcdCodeCreate(MutationBody):
    icdCode: str


class IcdCodeEdit(MutationBody):
    pass


class BiomarkerConfigCreate(MutationBody):
    gender: str
    age: str


class BiomarkerConfigEdit(MutationBody):
    pass
