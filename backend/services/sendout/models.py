"""Sendout model (PHI) — migrated from GkSendoutService (SendoutBatches)."""

from __future__ import annotations

from sqlalchemy import JSON, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base, TimestampMixin


class SendoutBatch(TimestampMixin, Base):
    __tablename__ = "SendoutBatches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sendoutLabId: Mapped[int | None] = mapped_column(Integer, index=True)
    sampleCount: Mapped[int | None] = mapped_column(Integer)
    panelIds: Mapped[list | None] = mapped_column(ARRAY(JSON))
    sampleIds: Mapped[list | None] = mapped_column(ARRAY(Integer))
    createdBy: Mapped[int | None] = mapped_column(Integer)
    # --- Added to match legacy AI-Portal V2 SendoutBatches schema (MIGRATION_GAPS.md) ---
    labName: Mapped[str | None] = mapped_column(String)
    testIds: Mapped[list | None] = mapped_column(ARRAY(JSON))
