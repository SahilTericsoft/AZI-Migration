"""Location models — migrated from GkFacilityService (Locations + links)."""

from sqlalchemy import JSON, Boolean, Index, Integer, String, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base, TimestampMixin


class Location(TimestampMixin, Base):
    __tablename__ = "Locations"
    # Expression indexes for the city/state list filters (addressDetails ->> ...).
    __table_args__ = (
        Index("ix_locations_addr_city", text("(\"addressDetails\" ->> 'city')")),
        Index("ix_locations_addr_state", text("(\"addressDetails\" ->> 'state')")),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    facilityId: Mapped[int | None] = mapped_column(Integer, index=True)
    name: Mapped[str | None] = mapped_column(String)
    type: Mapped[str | None] = mapped_column(String)
    code: Mapped[str | None] = mapped_column(String)
    adminId: Mapped[int | None] = mapped_column(Integer)
    addressDetails: Mapped[dict | None] = mapped_column(JSON)
    primaryContactDetails: Mapped[dict | None] = mapped_column(JSON)
    criticalDetails: Mapped[dict | None] = mapped_column(JSON)
    billingDetails: Mapped[dict | None] = mapped_column(JSON)
    emergencyContactDetails: Mapped[list | None] = mapped_column(ARRAY(JSON))
    accountPreferences: Mapped[dict | None] = mapped_column(JSON)
    labId: Mapped[int | None] = mapped_column(Integer)
    bloodDrawInformation: Mapped[dict | None] = mapped_column(JSON)
    panels: Mapped[list | None] = mapped_column(ARRAY(Integer))
    createdBy: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str | None] = mapped_column(String)
    isActive: Mapped[bool | None] = mapped_column(Boolean, default=True)
    internalLocationId: Mapped[str | None] = mapped_column(String)
    purpose: Mapped[str | None] = mapped_column(String)
    lastCompletedStep: Mapped[int | None] = mapped_column(Integer)


class LocationUser(TimestampMixin, Base):
    __tablename__ = "LocationUsers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    locationId: Mapped[int | None] = mapped_column(Integer, index=True)
    userId: Mapped[int | None] = mapped_column(Integer, index=True)


class LocationPhysician(TimestampMixin, Base):
    __tablename__ = "LocationPhysicians"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    locationId: Mapped[int | None] = mapped_column(Integer, index=True)
    physicianId: Mapped[int | None] = mapped_column(Integer, index=True)
    isActive: Mapped[bool | None] = mapped_column(Boolean, default=True)
