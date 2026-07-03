"""Result models (PHI) — migrated from GkPdfGeneratorService result entities."""

from __future__ import annotations

from sqlalchemy import JSON, Boolean, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base, TimestampMixin


class UploadResultSession(TimestampMixin, Base):
    """A result-entry session — one worklist + selected test/panel, manual or
    from an uploaded instrument run file. Groups ResultSamples / ResultControls."""

    __tablename__ = "UploadResultSessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    worklistId: Mapped[int | None] = mapped_column(Integer, index=True)
    worklistDetails: Mapped[dict | None] = mapped_column(JSON)
    testId: Mapped[int | None] = mapped_column(Integer)
    biomarkerId: Mapped[int | None] = mapped_column(Integer)
    testCode: Mapped[str | None] = mapped_column(String)  # selected panel(s)
    biomarkerCode: Mapped[str | None] = mapped_column(String)  # selected test(s)
    biomarkerDetails: Mapped[list | None] = mapped_column(JSON)  # [{id, name}]
    accessionIds: Mapped[list | None] = mapped_column(JSON)
    sampleType: Mapped[str | None] = mapped_column(String)
    status: Mapped[str | None] = mapped_column(String)  # draft/pendingReview/completed/discarded/rejected
    isManual: Mapped[bool | None] = mapped_column(Boolean)
    isDiscarded: Mapped[bool | None] = mapped_column(Boolean, default=False)
    fileName: Mapped[str | None] = mapped_column(String)
    runMetadata: Mapped[dict | None] = mapped_column(JSON)
    cqCutoff: Mapped[float | None] = mapped_column(Float)
    createdBy: Mapped[int | None] = mapped_column(Integer)
    createdByDetails: Mapped[dict | None] = mapped_column(JSON)


class ResultSample(TimestampMixin, Base):
    __tablename__ = "ResultSamples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uploadResultSessionId: Mapped[int | None] = mapped_column(Integer, index=True)
    accessionId: Mapped[str | None] = mapped_column(String)
    sampleId: Mapped[int | None] = mapped_column(Integer, index=True)
    orderId: Mapped[int | None] = mapped_column(Integer, index=True)
    isGenerated: Mapped[bool | None] = mapped_column(Boolean)
    testCode: Mapped[str | None] = mapped_column(String)
    biomarkerCode: Mapped[str | None] = mapped_column(String)
    # per-target reading (run-file) / per-biomarker value (manual)
    targetName: Mapped[str | None] = mapped_column(String)
    biomarkerName: Mapped[str | None] = mapped_column(String)
    fluorophore: Mapped[str | None] = mapped_column(String)
    wellPosition: Mapped[str | None] = mapped_column(String)
    cqValue: Mapped[float | None] = mapped_column(Float)
    result: Mapped[str | None] = mapped_column(String)
    value: Mapped[str | None] = mapped_column(String)
    isMarkForReview: Mapped[bool | None] = mapped_column(Boolean)
    reasonForRejection: Mapped[str | None] = mapped_column(Text)
    isManual: Mapped[bool | None] = mapped_column(Boolean)
    isRejected: Mapped[bool | None] = mapped_column(Boolean)
    isValid: Mapped[bool | None] = mapped_column(Boolean)
    isRerun: Mapped[bool | None] = mapped_column(Boolean)
    comments: Mapped[str | None] = mapped_column(Text)
    note: Mapped[str | None] = mapped_column(Text)
    pdfVariable: Mapped[dict | None] = mapped_column(JSON)
    reviewerNote: Mapped[str | None] = mapped_column(Text)


class ResultControl(TimestampMixin, Base):
    __tablename__ = "ResultControls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uploadResultSessionId: Mapped[int | None] = mapped_column(Integer, index=True)
    testPanelCode: Mapped[str | None] = mapped_column(String)
    wellPosition: Mapped[str | None] = mapped_column(String)
    control: Mapped[str | None] = mapped_column(String)
    targetName: Mapped[str | None] = mapped_column(String)
    biomarkerName: Mapped[str | None] = mapped_column(String)
    fluorophore: Mapped[str | None] = mapped_column(String)
    ctValue: Mapped[float | None] = mapped_column(Float)
    result: Mapped[str | None] = mapped_column(String)
    comments: Mapped[str | None] = mapped_column(Text)
    reasonForChange: Mapped[str | None] = mapped_column(Text)
