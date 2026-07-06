"""Legacy-parity tables — auto-generated from AI-Portal V2 Sequelize models.

These legacy tables had no equivalent in the initial AZI migration. They are
modeled here (id PK + createdAt/updatedAt via TimestampMixin) so the schema is a
complete 1:1 mirror of the legacy DB. Columns/types are derived from the source
Sequelize `.init()` definitions. Reserved/keyword column names use name= overrides.
"""

from __future__ import annotations

from datetime import datetime  # noqa: F401

from sqlalchemy import (
    JSON, BigInteger, Boolean, DateTime, Float, Integer, Numeric, String, Text,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base, TimestampMixin

