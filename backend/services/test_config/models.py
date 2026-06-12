"""Test Configuration models — the catalog of what can be ordered/measured.

Migrated from GkPanelService + GkLabOsService (Panels, Tests, Biomarkers) and
GkPanelService code lookups (CptCodes, IcdCodes). Columns follow the real
schema; names stay camelCase to match the live DB.
"""

from sqlalchemy import JSON, Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base, TimestampMixin


class Biomarker(TimestampMixin, Base):
    __tablename__ = "Biomarkers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String)
    code: Mapped[str | None] = mapped_column(String)
    sampleType: Mapped[str | None] = mapped_column(String)
    sampleCollectionDeviceName: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)
    reportFormat: Mapped[str | None] = mapped_column(String)
    isActive: Mapped[bool | None] = mapped_column(Boolean, default=True)
    status: Mapped[str | None] = mapped_column(String)
    createdBy: Mapped[int | None] = mapped_column(Integer)
    isConfigurationRequired: Mapped[bool | None] = mapped_column(Boolean)
    isPocConfigReq: Mapped[bool | None] = mapped_column(Boolean)
    pocConfigArr: Mapped[list | None] = mapped_column(ARRAY(String))
    biomarkerLayoutDetails: Mapped[list | None] = mapped_column(ARRAY(JSONB))
    isIndividuallyOffered: Mapped[bool | None] = mapped_column(Boolean)
    departmentIds: Mapped[list | None] = mapped_column(ARRAY(Integer))
    reagentIds: Mapped[list | None] = mapped_column(ARRAY(Integer))
    instrumentIds: Mapped[list | None] = mapped_column(ARRAY(Integer))


class Test(TimestampMixin, Base):
    __tablename__ = "Tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String)
    code: Mapped[str | None] = mapped_column(String)
    sampleType: Mapped[str | None] = mapped_column(String)
    sampleCollectionDeviceName: Mapped[str | None] = mapped_column(String)
    sampleQuantity: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)
    createdBy: Mapped[int | None] = mapped_column(Integer)
    isIntakeFormRequired: Mapped[bool | None] = mapped_column(Boolean)
    formId: Mapped[int | None] = mapped_column(Integer)
    isStateReportingRequired: Mapped[bool | None] = mapped_column(Boolean)
    stateReporting: Mapped[dict | None] = mapped_column(JSON)
    isBulkImportRequired: Mapped[bool | None] = mapped_column(Boolean)
    isActive: Mapped[bool | None] = mapped_column(Boolean, default=True)
    biomarkerIds: Mapped[list | None] = mapped_column(ARRAY(Integer))
    status: Mapped[str | None] = mapped_column(String)
    chatId: Mapped[int | None] = mapped_column(Integer)
    resultingMode: Mapped[str | None] = mapped_column(String)
    kitComponents: Mapped[list | None] = mapped_column(ARRAY(String))
    kitImages: Mapped[list | None] = mapped_column(ARRAY(String))
    questions: Mapped[list | None] = mapped_column(ARRAY(Integer))
    testLayoutDetails: Mapped[list | None] = mapped_column(ARRAY(JSON))
    icdCodes: Mapped[list | None] = mapped_column(ARRAY(Integer))
    isIcdCodeRequired: Mapped[bool | None] = mapped_column(Boolean)
    cptCodes: Mapped[list | None] = mapped_column(ARRAY(Integer))
    isCptCodeRequired: Mapped[bool | None] = mapped_column(Boolean)
    cptCodeDetails: Mapped[list | None] = mapped_column(ARRAY(JSON))
    testCategory: Mapped[str | None] = mapped_column(String)
    departmentIds: Mapped[list | None] = mapped_column(ARRAY(Integer))
    reagentIds: Mapped[list | None] = mapped_column(ARRAY(Integer))
    instrumentIds: Mapped[list | None] = mapped_column(ARRAY(Integer))


class Panel(TimestampMixin, Base):
    __tablename__ = "Panels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String)
    code: Mapped[str | None] = mapped_column(String)
    testIds: Mapped[list | None] = mapped_column(ARRAY(Integer))
    description: Mapped[str | None] = mapped_column(Text)
    isActive: Mapped[bool | None] = mapped_column(Boolean, default=True)
    status: Mapped[str | None] = mapped_column(String)
    createdBy: Mapped[int | None] = mapped_column(Integer)
    sampleType: Mapped[str | None] = mapped_column(String)
    biomarkerIds: Mapped[list | None] = mapped_column(ARRAY(Integer))
    internalPanelId: Mapped[str | None] = mapped_column(String)


class CptCode(TimestampMixin, Base):
    __tablename__ = "CptCodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cptCode: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)


class IcdCode(TimestampMixin, Base):
    __tablename__ = "IcdCodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    icdCode: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String)
