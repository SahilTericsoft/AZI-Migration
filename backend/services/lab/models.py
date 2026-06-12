"""Lab models — migrated from GkLabService / GkLabOsService."""

from __future__ import annotations

from sqlalchemy import JSON, Boolean, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base, TimestampMixin


class Lab(TimestampMixin, Base):
    __tablename__ = "Labs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String)
    code: Mapped[str | None] = mapped_column(String)
    labExternalId: Mapped[str | None] = mapped_column(String)
    npiNumber: Mapped[str | None] = mapped_column(String)
    cliaId: Mapped[str | None] = mapped_column(String)
    capId: Mapped[str | None] = mapped_column(String)
    colaId: Mapped[str | None] = mapped_column(String)
    labType: Mapped[str | None] = mapped_column(String)
    isSdiLab: Mapped[bool | None] = mapped_column(Boolean)
    isActive: Mapped[bool | None] = mapped_column(Boolean, default=True)
    emailId: Mapped[str | None] = mapped_column(String)
    status: Mapped[str | None] = mapped_column(String)
    mobileNumber: Mapped[str | None] = mapped_column(String)
    secondaryMobileNumber: Mapped[str | None] = mapped_column(String)
    faxNumber: Mapped[str | None] = mapped_column(String)
    addressLine1: Mapped[str | None] = mapped_column(String)
    addressLine2: Mapped[str | None] = mapped_column(String)
    zipcode: Mapped[str | None] = mapped_column(String)
    state: Mapped[str | None] = mapped_column(String)
    city: Mapped[str | None] = mapped_column(String)
    adminId: Mapped[int | None] = mapped_column(Integer)
    createdBy: Mapped[int | None] = mapped_column(Integer)
    logo: Mapped[dict | None] = mapped_column(JSON)
    themeColor: Mapped[str | None] = mapped_column(String)
    directorDetails: Mapped[dict | None] = mapped_column(JSON)
    lastCompletedStep: Mapped[int | None] = mapped_column(Integer)
    labRole: Mapped[str | None] = mapped_column(String)
    referenceFacilityId: Mapped[int | None] = mapped_column(Integer)
    referenceLocationId: Mapped[int | None] = mapped_column(Integer)


class LabUser(TimestampMixin, Base):
    __tablename__ = "LabUsers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    labId: Mapped[int | None] = mapped_column(Integer, index=True)
    userId: Mapped[int | None] = mapped_column(Integer, index=True)
    locationIds: Mapped[list | None] = mapped_column(ARRAY(Integer))
