"""Facility models — migrated from GkFacilityService."""

from __future__ import annotations

from sqlalchemy import JSON, Boolean, Index, Integer, String, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base, TimestampMixin


class Facility(TimestampMixin, Base):
    __tablename__ = "Facilities"
    # Expression indexes so the city/state list filters (addressDetails ->> ...)
    # use an index instead of scanning + extracting JSON on every row.
    __table_args__ = (
        Index("ix_facilities_addr_city", text("(\"addressDetails\" ->> 'city')")),
        Index("ix_facilities_addr_state", text("(\"addressDetails\" ->> 'state')")),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String)
    code: Mapped[str | None] = mapped_column(String)
    type: Mapped[str | None] = mapped_column(String)
    primaryContactDetails: Mapped[dict | None] = mapped_column(JSON)
    panels: Mapped[list | None] = mapped_column(ARRAY(Integer))
    physicians: Mapped[list | None] = mapped_column(ARRAY(Integer))
    adminId: Mapped[int | None] = mapped_column(Integer)
    addressDetails: Mapped[dict | None] = mapped_column(JSON)
    createdBy: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str | None] = mapped_column(String)
    isActive: Mapped[bool | None] = mapped_column(Boolean, default=True)
    isDroidAllowed: Mapped[bool | None] = mapped_column(Boolean)
    allowAdvancedFunctionality: Mapped[bool | None] = mapped_column(Boolean)
    lastCompletedStep: Mapped[int | None] = mapped_column(Integer)
    isInsuranceImageRequired: Mapped[bool | None] = mapped_column(Boolean)
    referenceLabId: Mapped[int | None] = mapped_column(Integer)


class FacilityUser(TimestampMixin, Base):
    __tablename__ = "FacilityUsers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    facilityId: Mapped[int | None] = mapped_column(Integer, index=True)
    userId: Mapped[int | None] = mapped_column(Integer, index=True)
    locationIds: Mapped[list | None] = mapped_column(ARRAY(Integer))
