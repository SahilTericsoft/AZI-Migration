"""Direct-to-Consumer models (PHI) — migrated from GkD2CService.

Customers order health kits, so customer/address/order data is PHI: protected +
audited. Customer `password` is masked.
"""

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base, TimestampMixin

CUSTOMER_SENSITIVE = {"password"}


class Customer(TimestampMixin, Base):
    __tablename__ = "Customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firstName: Mapped[str | None] = mapped_column(String)
    lastName: Mapped[str | None] = mapped_column(String)
    dateOfBirth: Mapped[str | None] = mapped_column(String)
    mobileNumber: Mapped[str | None] = mapped_column(String)
    emailId: Mapped[str | None] = mapped_column(String, index=True)
    password: Mapped[str | None] = mapped_column(String)
    patientId: Mapped[int | None] = mapped_column(Integer)
    isVerified: Mapped[bool | None] = mapped_column(Boolean)
    isActive: Mapped[bool | None] = mapped_column(Boolean, default=True)


class CustomerAddress(TimestampMixin, Base):
    __tablename__ = "CustomerAddresses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    address1: Mapped[str | None] = mapped_column(String)
    address2: Mapped[str | None] = mapped_column(String)
    zipcode: Mapped[int | None] = mapped_column(Integer)
    state: Mapped[str | None] = mapped_column(String)
    county: Mapped[str | None] = mapped_column(String)
    city: Mapped[str | None] = mapped_column(String)
    mobileNumber: Mapped[str | None] = mapped_column(String)
    isDefault: Mapped[bool | None] = mapped_column(Boolean)
    addedBy: Mapped[int | None] = mapped_column(Integer)
    customerId: Mapped[int | None] = mapped_column(Integer, index=True)


class CustomerCart(TimestampMixin, Base):
    __tablename__ = "CustomerCarts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    productId: Mapped[float | None] = mapped_column(Numeric)
    quantity: Mapped[float | None] = mapped_column(Numeric)
    addedBy: Mapped[float | None] = mapped_column(Numeric)


class D2COrder(TimestampMixin, Base):
    __tablename__ = "D2C_CustomerOrders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    orderCode: Mapped[str | None] = mapped_column(String, index=True)
    customerId: Mapped[float | None] = mapped_column(Numeric)
    patientId: Mapped[float | None] = mapped_column(Numeric)
    dateOfOrder: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    paymentStatus: Mapped[str | None] = mapped_column(String)
    paymentDate: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    paymentMode: Mapped[str | None] = mapped_column(String)
    address: Mapped[dict | None] = mapped_column(JSON)
    summary: Mapped[dict | None] = mapped_column(JSON)
