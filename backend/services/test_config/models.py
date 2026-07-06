"""Test Configuration models — the catalog of what can be ordered/measured.

Migrated from GkPanelService + GkLabOsService (Panels, Tests, Biomarkers) and
GkPanelService code lookups (CptCodes, IcdCodes). Columns follow the real
schema; names stay camelCase to match the live DB.
"""

from __future__ import annotations

from sqlalchemy import JSON, Boolean, Integer, Numeric, String, Text
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
    # --- Added to match legacy AI-Portal V2 Biomarkers schema (MIGRATION_GAPS.md) ---
    internalBiomarkerId: Mapped[str | None] = mapped_column(String)


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
    # --- Added to match legacy AI-Portal V2 Tests schema (MIGRATION_GAPS.md) ---
    reportFormat: Mapped[str | None] = mapped_column(String)
    alertLimit: Mapped[float | None] = mapped_column(Numeric)
    maxLimit: Mapped[float | None] = mapped_column(Numeric)
    hasOrderingLimit: Mapped[bool | None] = mapped_column(Boolean)
    isLinkedTest: Mapped[bool | None] = mapped_column(Boolean)
    linkedTestId: Mapped[float | None] = mapped_column(Numeric)
    linkedTestText: Mapped[str | None] = mapped_column(String)
    internalTestId: Mapped[str | None] = mapped_column(String)
    integrationDetails: Mapped[dict | None] = mapped_column(JSON)
    loincCode: Mapped[str | None] = mapped_column(String)
    lastBarcodeCount: Mapped[int | None] = mapped_column(Integer)
    processOverView: Mapped[str | None] = mapped_column(String)
    videoUrl: Mapped[str | None] = mapped_column(String)
    kitRedirectUrl: Mapped[str | None] = mapped_column(String)
    normalPdfTemplatePath: Mapped[str | None] = mapped_column(String)
    abnormalPdfTemplatePath: Mapped[str | None] = mapped_column(String)


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
    # Per-patient monthly ordering limits. A patient is "alert"-flagged when their
    # order count for this panel in the current month reaches alertLimit, and
    # "max"-flagged when it reaches maxLimit.
    hasOrderingLimit: Mapped[bool | None] = mapped_column(Boolean, default=False)
    alertLimit: Mapped[int | None] = mapped_column(Integer)
    maxLimit: Mapped[int | None] = mapped_column(Integer)


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
