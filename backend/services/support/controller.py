"""Controllers for the Support service (Help Center + Resources documents)."""

from __future__ import annotations

from fastapi import HTTPException

from core.api import ok
from core.controller import BaseController
from services.support.models import HelpSection, SystemDocument


class DocumentController(BaseController):
    model = SystemDocument
    name = "Document"
    search_fields = ("title", "description")

    def add(self, data: dict) -> dict:
        title = (data.get("title") or "").strip()
        url = (data.get("url") or "").strip()
        if not title or not url:
            raise HTTPException(400, "title and url are required")
        payload = self.writable({**data, "title": title, "url": url})
        payload.setdefault("isActive", True)
        row = SystemDocument(**payload)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return ok(self.serialize(row), "Document added successfully")


class HelpSectionController(BaseController):
    model = HelpSection
    name = "Help section"
    search_fields = ("title",)

    def listing(self) -> dict:
        rows = (
            self.db.query(HelpSection)
            .filter(HelpSection.isActive.is_(True))
            .order_by(HelpSection.sequence)
            .all()
        )
        return ok([self.serialize(r) for r in rows], "Help sections")

    def add(self, data: dict) -> dict:
        payload = self.writable(data)
        payload.setdefault("isActive", True)
        row = HelpSection(**payload)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return ok(self.serialize(row), "Help section added")
