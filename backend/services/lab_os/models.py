"""Lab Operations models — migrated from GkLabOsService.

Departments, Instruments, SOPs, Validations and lab processing sessions. Several
legacy columns are snake_case (kept as-is to match the DB).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base, TimestampMixin


class Department(TimestampMixin, Base):
    __tablename__ = "Departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String)
    code: Mapped[str | None] = mapped_column(String)
    createdBy: Mapped[int | None] = mapped_column(Integer)
    reportType: Mapped[list | None] = mapped_column(ARRAY(String))
    reportFormat: Mapped[list | None] = mapped_column(ARRAY(String))
    isActive: Mapped[bool | None] = mapped_column(Boolean, default=True)


class Instrument(TimestampMixin, Base):
    __tablename__ = "Instruments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    instrument: Mapped[str | None] = mapped_column(String)
    asset_number: Mapped[str | None] = mapped_column(String)
    location: Mapped[str | None] = mapped_column(String)
    manufacturer: Mapped[str | None] = mapped_column(String)
    category: Mapped[str | None] = mapped_column(String)
    model: Mapped[str | None] = mapped_column(String)
    serial_number: Mapped[str | None] = mapped_column(String)
    purchase_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_calibration_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_calibration_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    calibration_frequency: Mapped[str | None] = mapped_column(String)
    calibration_type: Mapped[str | None] = mapped_column(String)
    vendor_name: Mapped[str | None] = mapped_column(String)
    vendor_email_address: Mapped[str | None] = mapped_column(String)
    created_by: Mapped[int | None] = mapped_column(Integer)
    labId: Mapped[int | None] = mapped_column(Integer)
    isLinked: Mapped[bool | None] = mapped_column(Boolean)
    plateType: Mapped[str | None] = mapped_column(String)
    status: Mapped[str | None] = mapped_column(String)


class Sop(TimestampMixin, Base):
    __tablename__ = "Sops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sop_name: Mapped[str | None] = mapped_column(String)
    sop_number: Mapped[str | None] = mapped_column(String)
    reviewer_name: Mapped[str | None] = mapped_column(String)
    date_of_review: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[int | None] = mapped_column(Integer)
    labId: Mapped[int | None] = mapped_column(Integer)


class Validation(TimestampMixin, Base):
    __tablename__ = "Validations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_of_document: Mapped[str | None] = mapped_column(String)
    test_id: Mapped[int | None] = mapped_column(Integer)
    biomarker_cutoff_value: Mapped[dict | None] = mapped_column(JSON)
    created_by: Mapped[int | None] = mapped_column(Integer)
    labId: Mapped[int | None] = mapped_column(Integer)


class LabSession(TimestampMixin, Base):
    __tablename__ = "LabSessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    step_id: Mapped[int | None] = mapped_column(Integer)
    sample_config: Mapped[dict | None] = mapped_column(JSON)
    created_by: Mapped[int | None] = mapped_column(Integer)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rack_number: Mapped[str | None] = mapped_column(String)
    status: Mapped[str | None] = mapped_column(String)
    comments: Mapped[str | None] = mapped_column(String)
    controls: Mapped[dict | None] = mapped_column(JSON)
    workflow_id: Mapped[int | None] = mapped_column(Integer)
    sample_count: Mapped[int | None] = mapped_column(Integer)
    protocol_type: Mapped[str | None] = mapped_column(String)
    lab_id: Mapped[int | None] = mapped_column(Integer)
    is_processed: Mapped[bool | None] = mapped_column(Boolean)
    orderType: Mapped[str | None] = mapped_column(String)
