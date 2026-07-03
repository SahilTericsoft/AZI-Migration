"""Request schemas for the Support service."""

from __future__ import annotations

from core.api import MutationBody


class DocumentCreate(MutationBody):
    title: str
    url: str


class HelpSectionCreate(MutationBody):
    title: str
