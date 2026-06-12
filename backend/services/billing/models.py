"""Billing reference models — migrated from GkPatientService billing refs."""

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base, TimestampMixin


class Insurer(TimestampMixin, Base):
    __tablename__ = "Insurers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str | None] = mapped_column(String)
    code: Mapped[str | None] = mapped_column(String)
    payerId: Mapped[str | None] = mapped_column(String)


class ClearingHouse(TimestampMixin, Base):
    __tablename__ = "ClearingHouses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clearingHouse: Mapped[str | None] = mapped_column(String)
    clearingHouseCode: Mapped[str | None] = mapped_column(String)
    isActive: Mapped[bool | None] = mapped_column(Boolean, default=True)
    createdBy: Mapped[int | None] = mapped_column(Integer)


class ClearingHouseInsurance(TimestampMixin, Base):
    __tablename__ = "ClearingHouseInsurances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clearingHouseId: Mapped[int | None] = mapped_column(Integer, index=True)
    payerName: Mapped[str | None] = mapped_column(String)
    payerId: Mapped[str | None] = mapped_column(String)
    CPID: Mapped[str | None] = mapped_column(String)
    type: Mapped[str | None] = mapped_column(String)
    groupId: Mapped[str | None] = mapped_column(String)
    realTimePayerId: Mapped[str | None] = mapped_column(String)
