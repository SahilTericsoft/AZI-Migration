"""State reporting models (PHI) — migrated from GkStateReportingService."""

from __future__ import annotations

from sqlalchemy import JSON, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base, TimestampMixin


class StateReporting(TimestampMixin, Base):
    __tablename__ = "StateReportings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    panelDetails: Mapped[dict | None] = mapped_column(JSON)
    sampleIds: Mapped[list | None] = mapped_column(ARRAY(Integer))
    reportingTime: Mapped[str | None] = mapped_column(String)
    status: Mapped[str | None] = mapped_column(String)
    attachment: Mapped[dict | None] = mapped_column(JSON)


class StateReportingSession(TimestampMixin, Base):
    __tablename__ = "StateReportingSessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stateReportingId: Mapped[int | None] = mapped_column(Integer, index=True)
    attempt: Mapped[int | None] = mapped_column(Integer)
    reportingTime: Mapped[str | None] = mapped_column(String)
    status: Mapped[str | None] = mapped_column(String)
    reason: Mapped[str | None] = mapped_column(String)
    responseData: Mapped[dict | None] = mapped_column(JSON)
