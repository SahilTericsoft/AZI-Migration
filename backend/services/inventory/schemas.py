"""Request schemas for the Inventory service."""

from __future__ import annotations

from pydantic import BaseModel

from core.api import MutationBody


class ProductCreate(MutationBody):
    name: str


class ProductEdit(MutationBody):
    pass


class ItemCreate(MutationBody):
    name: str


class ItemEdit(MutationBody):
    pass


class SubItemCreate(MutationBody):
    inventoryItemId: int
    name: str


class SubItemEdit(MutationBody):
    pass


class QuantityCreate(MutationBody):
    itemId: int


class QuantityEdit(MutationBody):
    pass


class SimpleCreate(MutationBody):
    pass


class InventoryListQuery(BaseModel):
    page: int | None = None
    limit: int | None = None
    search: str | None = None
    isActive: bool | None = None
    department: int | None = None
    lowStock: bool | None = None
