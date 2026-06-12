"""Inventory models — consolidates GkInventoryService + GkLabInventoryService.

InventoryQuantity legacy `order` column is renamed to `orderInfo` (reserved
word). Products soft-delete via isDeleted.
"""

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base, TimestampMixin


class Product(TimestampMixin, Base):
    __tablename__ = "Products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String)
    panelId: Mapped[int | None] = mapped_column(Integer)
    productCode: Mapped[str | None] = mapped_column(String)
    quantity: Mapped[int | None] = mapped_column(Integer)
    alertLevelStock: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(String)
    tagLine: Mapped[str | None] = mapped_column(String)
    methodOfCollection: Mapped[str | None] = mapped_column(String)
    resultingDays: Mapped[str | None] = mapped_column(String)
    analytes: Mapped[list | None] = mapped_column(ARRAY(String))
    price: Mapped[int | None] = mapped_column(Integer)
    isActive: Mapped[bool | None] = mapped_column(Boolean, default=True)
    isDeleted: Mapped[bool | None] = mapped_column(Boolean, default=False)
    addedBy: Mapped[int | None] = mapped_column(Integer)
    productCatalogLink: Mapped[str | None] = mapped_column(String)


class ProductImage(TimestampMixin, Base):
    __tablename__ = "ProductImages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    productId: Mapped[int | None] = mapped_column(Integer, index=True)
    mimeType: Mapped[str | None] = mapped_column(String)
    secureUrl: Mapped[str | None] = mapped_column(String)
    fileName: Mapped[str | None] = mapped_column(String)


class QrCode(TimestampMixin, Base):
    __tablename__ = "QrCodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str | None] = mapped_column(String, index=True)
    qrData: Mapped[str | None] = mapped_column(String)
    facilityId: Mapped[int | None] = mapped_column(Integer)
    locationId: Mapped[int | None] = mapped_column(Integer)
    panelId: Mapped[int | None] = mapped_column(Integer)
    physicianId: Mapped[int | None] = mapped_column(Integer)
    createdBy: Mapped[int | None] = mapped_column(Integer)
    isActive: Mapped[bool | None] = mapped_column(Boolean, default=True)
    type: Mapped[str | None] = mapped_column(String)
    flow: Mapped[str | None] = mapped_column(String)
    caption: Mapped[str | None] = mapped_column(Text)
    imageDetails: Mapped[dict | None] = mapped_column(JSON)
    billingMode: Mapped[str | None] = mapped_column(String)


class Barcode(TimestampMixin, Base):
    __tablename__ = "Barcodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    barcode: Mapped[str | None] = mapped_column(String, index=True)
    testId: Mapped[int | None] = mapped_column(Integer)
    testName: Mapped[str | None] = mapped_column(String)
    purpose: Mapped[str | None] = mapped_column(String)
    isAvailable: Mapped[bool | None] = mapped_column(Boolean)


class BarcodeSession(TimestampMixin, Base):
    __tablename__ = "BarcodeSessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str | None] = mapped_column(String)
    attachmentDetails: Mapped[dict | None] = mapped_column(JSON)
    testName: Mapped[str | None] = mapped_column(String)
    testId: Mapped[int | None] = mapped_column(Integer)
    quantity: Mapped[int | None] = mapped_column(Integer)
    createdByDetails: Mapped[dict | None] = mapped_column(JSON)


class InventoryItem(TimestampMixin, Base):
    __tablename__ = "InventoryItems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String)
    type: Mapped[str | None] = mapped_column(String)
    quantity: Mapped[int | None] = mapped_column(Integer)
    department: Mapped[int | None] = mapped_column(Integer)
    category: Mapped[str | None] = mapped_column(String)
    units: Mapped[str | None] = mapped_column(String)
    storageLocation: Mapped[str | None] = mapped_column(String)
    alertQuantity: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)
    createdBy: Mapped[int | None] = mapped_column(Integer)
    image: Mapped[dict | None] = mapped_column(JSON)
    isSubItems: Mapped[bool | None] = mapped_column(Boolean)
    isActive: Mapped[bool | None] = mapped_column(Boolean, default=True)
    status: Mapped[str | None] = mapped_column(String)


class InventorySubItem(TimestampMixin, Base):
    __tablename__ = "InventorySubItems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inventoryItemId: Mapped[int | None] = mapped_column(Integer, index=True)
    name: Mapped[str | None] = mapped_column(String)
    units: Mapped[str | None] = mapped_column(String)
    alertQuantity: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)
    image: Mapped[dict | None] = mapped_column(JSON)
    quantity: Mapped[int | None] = mapped_column(Integer)


class InventoryQuantity(TimestampMixin, Base):
    __tablename__ = "InventoryQuantities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subItemId: Mapped[int | None] = mapped_column(Integer)
    itemId: Mapped[int | None] = mapped_column(Integer, index=True)
    lotNumber: Mapped[str | None] = mapped_column(String)
    quantity: Mapped[int | None] = mapped_column(Integer)
    expiaryDate: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    manufacturer: Mapped[str | None] = mapped_column(String)
    batch: Mapped[str | None] = mapped_column(String)
    catalog: Mapped[str | None] = mapped_column(String)
    price: Mapped[str | None] = mapped_column(String)
    orderInfo: Mapped[dict | None] = mapped_column(JSON)
    event: Mapped[str | None] = mapped_column(String)
    reason: Mapped[str | None] = mapped_column(Text)
    isRemoved: Mapped[bool | None] = mapped_column(Boolean)
    createdBy: Mapped[int | None] = mapped_column(Integer)


class InventoryStaticData(TimestampMixin, Base):
    __tablename__ = "InventoryStaticData"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str | None] = mapped_column(String, index=True)
    value: Mapped[list | None] = mapped_column(ARRAY(JSON))
