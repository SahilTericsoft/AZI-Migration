"""Integration models — external-system credentials & config.

AdvancedMD (GkAdvancedMDService/GkPatientService) + OCR config (GkOCRService).
The `token` is a secret and is excluded from API responses.
"""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base, TimestampMixin

ADVANCEDMD_SENSITIVE = {"token"}


class AdvancedMDToken(TimestampMixin, Base):
    __tablename__ = "AdvancedMDTokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    userName: Mapped[str | None] = mapped_column(String)
    loginPageUrl: Mapped[str | None] = mapped_column(String)
    officeKey: Mapped[str | None] = mapped_column(String)
    token: Mapped[str | None] = mapped_column(Text)
    expiry: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class OcrCompany(TimestampMixin, Base):
    __tablename__ = "OCRCompanies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    image: Mapped[dict | None] = mapped_column(JSON)
    companyName: Mapped[str | None] = mapped_column(String)
    config: Mapped[dict | None] = mapped_column(JSON)
    addedBy: Mapped[int | None] = mapped_column(Integer)


class OcrSetting(TimestampMixin, Base):
    __tablename__ = "OCRSettings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str | None] = mapped_column(String)
    code: Mapped[str | None] = mapped_column(String)
    addedBy: Mapped[float | None] = mapped_column(Numeric)
