"""Sample model (PHI) — migrated from GkTestOrderService/GkBulkUploadService (OrderSamples).

Focused on the clinically/operationally important columns of the 56-column
legacy table (identity, order/panel refs, status, collection, barcode,
accession, result flags).
"""

from sqlalchemy import JSON, Boolean, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base, TimestampMixin


class OrderSample(TimestampMixin, Base):
    __tablename__ = "OrderSamples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sampleCode: Mapped[str | None] = mapped_column(String, index=True)
    orderId: Mapped[int | None] = mapped_column(Integer, index=True)
    orderDetails: Mapped[dict | None] = mapped_column(JSON)
    panelId: Mapped[int | None] = mapped_column(Integer)
    panelDetails: Mapped[dict | None] = mapped_column(JSON)
    physicianId: Mapped[int | None] = mapped_column(Integer)
    physicianDetails: Mapped[dict | None] = mapped_column(JSON)
    sampleType: Mapped[str | None] = mapped_column(String)
    billingMode: Mapped[str | None] = mapped_column(String)
    externalReferenceNumber: Mapped[str | None] = mapped_column(String)
    insuranceDetails: Mapped[dict | None] = mapped_column(JSON)
    rejectionDetails: Mapped[dict | None] = mapped_column(JSON)
    status: Mapped[str | None] = mapped_column(String)
    resultedMode: Mapped[str | None] = mapped_column(String)
    isIntakeFormCompleted: Mapped[bool | None] = mapped_column(Boolean)
    isSubmitted: Mapped[bool | None] = mapped_column(Boolean)
    isConsentSigned: Mapped[bool | None] = mapped_column(Boolean)
    isEnbChecked: Mapped[bool | None] = mapped_column(Boolean)
    isSendOut: Mapped[bool | None] = mapped_column(Boolean)
    sendOutLabDetails: Mapped[dict | None] = mapped_column(JSON)
    icdCodes: Mapped[list | None] = mapped_column(ARRAY(String))
    icdCodeDetails: Mapped[list | None] = mapped_column(ARRAY(JSON))
    dateOfCollection: Mapped[str | None] = mapped_column(String)
    timeOfCollection: Mapped[str | None] = mapped_column(String)
    dateTimeOfCollection: Mapped[str | None] = mapped_column(String)
    isPriorityOrder: Mapped[bool | None] = mapped_column(Boolean)
    isPaymentCompleted: Mapped[bool | None] = mapped_column(Boolean)
    typeOfBarcode: Mapped[str | None] = mapped_column(String)
    barcode: Mapped[str | None] = mapped_column(String)
    patientBarcode: Mapped[str | None] = mapped_column(String)
    labBarcode: Mapped[str | None] = mapped_column(String)
    isBarcodeReplaced: Mapped[bool | None] = mapped_column(Boolean)
    isAccessioned: Mapped[bool | None] = mapped_column(Boolean)
    isStateReported: Mapped[bool | None] = mapped_column(Boolean)
    statusTimeLine: Mapped[list | None] = mapped_column(ARRAY(JSON))
    createdBy: Mapped[int | None] = mapped_column(Integer)
    accessionedBy: Mapped[int | None] = mapped_column(Integer)
    accessionedLabId: Mapped[int | None] = mapped_column(Integer)
    isPdfGenerated: Mapped[bool | None] = mapped_column(Boolean)
    pdfGeneratedDate: Mapped[str | None] = mapped_column(String)
    resultSentToPatient: Mapped[bool | None] = mapped_column(Boolean)
    accessionedDate: Mapped[str | None] = mapped_column(String)
    pdfDetails: Mapped[dict | None] = mapped_column(JSON)
    results: Mapped[dict | None] = mapped_column(JSON)
    source: Mapped[str | None] = mapped_column(String)
