"""ORM models for the User service.

Tables, columns and types mirror the real schema (all-tables-schema.sql /
GkUserService Sequelize models) so this maps onto the existing database with no
data migration. Column names stay camelCase to match the live DB.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class TimestampMixin:
    createdAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class User(TimestampMixin, Base):
    __tablename__ = "Users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prefix: Mapped[str | None] = mapped_column(String)
    suffix: Mapped[str | None] = mapped_column(String)
    firstName: Mapped[str | None] = mapped_column(String)
    middleName: Mapped[str | None] = mapped_column(String)
    lastName: Mapped[str | None] = mapped_column(String)
    mobileNumber: Mapped[str | None] = mapped_column(String)
    secondaryMobileNumber: Mapped[str | None] = mapped_column(String)
    mobileNumberCode: Mapped[str | None] = mapped_column(String)
    faxNumber: Mapped[str | None] = mapped_column(String)
    addressLine1: Mapped[str | None] = mapped_column(String)
    addressLine2: Mapped[str | None] = mapped_column(String)
    dateOfBirth: Mapped[str | None] = mapped_column(String)
    zipcode: Mapped[str | None] = mapped_column(String)
    state: Mapped[str | None] = mapped_column(String)
    city: Mapped[str | None] = mapped_column(String)
    emailId: Mapped[str | None] = mapped_column(String, index=True)
    npiNumber: Mapped[str | None] = mapped_column(String)
    pTanNumber: Mapped[str | None] = mapped_column(String)
    specialityType: Mapped[str | None] = mapped_column(String)
    tinNumber: Mapped[str | None] = mapped_column(String)
    designation: Mapped[str | None] = mapped_column(String)
    gender: Mapped[str | None] = mapped_column(String)
    roleId: Mapped[int | None] = mapped_column(Integer)
    roleObj: Mapped[dict | None] = mapped_column(JSON)
    password: Mapped[str | None] = mapped_column(String)
    isSdiUser: Mapped[bool | None] = mapped_column(Boolean)
    isPhysician: Mapped[bool | None] = mapped_column(Boolean)
    taxonomyDetails: Mapped[dict | None] = mapped_column(JSON)
    isSameAddress: Mapped[bool | None] = mapped_column(Boolean)
    isActive: Mapped[bool | None] = mapped_column(Boolean)
    isEmailVerified: Mapped[bool | None] = mapped_column(Boolean)
    isDeleted: Mapped[bool | None] = mapped_column(Boolean)
    createdBy: Mapped[int | None] = mapped_column(Integer)
    isHybrid: Mapped[bool | None] = mapped_column(Boolean, default=False)
    signature: Mapped[str | None] = mapped_column(Text)
    signatureCount: Mapped[int | None] = mapped_column(Integer)
    internalUserId: Mapped[str | None] = mapped_column(String)


class Role(TimestampMixin, Base):
    __tablename__ = "Roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str | None] = mapped_column(String)
    code: Mapped[str | None] = mapped_column(String)
    isSdiRole: Mapped[bool | None] = mapped_column(Boolean)
    isSignatureRequired: Mapped[bool | None] = mapped_column(Boolean)


class Token(TimestampMixin, Base):
    __tablename__ = "Tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    userId: Mapped[int | None] = mapped_column(Integer, index=True)
    token: Mapped[str | None] = mapped_column(Text)
    expiryTime: Mapped[str | None] = mapped_column(String)
    isActive: Mapped[bool | None] = mapped_column(Boolean)


class AclModule(TimestampMixin, Base):
    __tablename__ = "ACLModulesMappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    module: Mapped[str | None] = mapped_column(String)
    feature: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String)
    code: Mapped[str | None] = mapped_column(String)
    apis: Mapped[list | None] = mapped_column(ARRAY(String))
    isPrimary: Mapped[bool | None] = mapped_column(Boolean)


class RoleAcl(TimestampMixin, Base):
    __tablename__ = "RoleAclModels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    roleId: Mapped[int | None] = mapped_column(Integer, index=True)
    moduleAccess: Mapped[str | None] = mapped_column(String)
    featureAccess: Mapped[str | None] = mapped_column(String)
    apiAccess: Mapped[list | None] = mapped_column(ARRAY(String))


class UserAcl(TimestampMixin, Base):
    __tablename__ = "UserAclModels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    userId: Mapped[int | None] = mapped_column(Integer, index=True)
    moduleAccess: Mapped[str | None] = mapped_column(String)
    featureAccess: Mapped[str | None] = mapped_column(String)
    apiAccess: Mapped[list | None] = mapped_column(ARRAY(String))
    roleId: Mapped[int | None] = mapped_column(Integer)


class StateCityStaticData(TimestampMixin, Base):
    """Geo reference data (city / state / zipcode / county / timezone)."""

    __tablename__ = "StateCityStaticData"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city: Mapped[str | None] = mapped_column(String)
    state: Mapped[str | None] = mapped_column(String)
    zipcode: Mapped[str | None] = mapped_column(String, index=True)
    timezone: Mapped[str | None] = mapped_column(String)
    isActive: Mapped[str | None] = mapped_column(String)  # STRING in the real schema
    county: Mapped[str | None] = mapped_column(String)
    country: Mapped[str | None] = mapped_column(String)


class Dropdown(TimestampMixin, Base):
    """Keyed dropdown sets (prefix / suffix / maritalStatus / race / ethnicity …).

    Legacy model file RaceandEthnicityModel.ts -> table "UserStaticData".
    `value` is a JSON array of option objects ({code, label, ...}).
    """

    __tablename__ = "UserStaticData"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str | None] = mapped_column(String, index=True)
    value: Mapped[list | None] = mapped_column(ARRAY(JSON))


class SystemConfig(TimestampMixin, Base):
    __tablename__ = "SystemConfigs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str | None] = mapped_column(String)
    billingReportHeaders: Mapped[list | None] = mapped_column(ARRAY(JSON))
    patientsReportHeaders: Mapped[list | None] = mapped_column(ARRAY(JSON))
    logo: Mapped[dict | None] = mapped_column(JSON)
    miniLogo: Mapped[dict | None] = mapped_column(JSON)
    url: Mapped[str | None] = mapped_column(String)
    labConfiguration: Mapped[dict | None] = mapped_column(JSON)
