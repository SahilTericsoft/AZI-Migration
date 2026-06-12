"""Controllers for the Inventory service (general + lab inventory).

Ported from GkInventoryService + GkLabInventoryService. Real business logic:
  * item / sub-item / product name uniqueness ("… already exists")
  * `isLowStock` derived from quantity vs alertQuantity
  * draft/active defaults, soft-delete for products, toggle for items
  * sub-items + lot-number lookups scoped to an item
"""

from fastapi import HTTPException
from sqlalchemy import func, or_

from core.api import ok, paginate
from core.controller import BaseController
from services.inventory.models import (
    Barcode,
    BarcodeSession,
    InventoryItem,
    InventoryQuantity,
    InventoryStaticData,
    InventorySubItem,
    Product,
    ProductImage,
    QrCode,
)


def _low_stock(quantity, alert) -> bool:
    return quantity is not None and alert is not None and quantity <= alert


class ProductController(BaseController):
    model = Product
    name = "Product"
    search_fields = ("name", "productCode")

    def add(self, data: dict) -> dict:
        name = (data.get("name") or "").strip()
        if not name:
            raise HTTPException(400, "name is required")
        if (
            self.db.query(Product)
            .filter(func.lower(Product.name) == name.lower(), Product.isDeleted.isnot(True))
            .first()
        ):
            raise HTTPException(409, "Product name already exists")
        payload = self.writable({**data, "name": name})
        payload.setdefault("isActive", True)
        payload.setdefault("isDeleted", False)
        product = Product(**payload)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return ok(self.serialize(product), "Product added successfully")


class ItemController(BaseController):
    model = InventoryItem
    name = "Inventory item"
    search_fields = ("name", "category")

    def add(self, data: dict) -> dict:
        name = (data.get("name") or "").strip()
        if not name:
            raise HTTPException(400, "name is required")
        if (
            self.db.query(InventoryItem)
            .filter(func.lower(InventoryItem.name) == name.lower())
            .first()
        ):
            raise HTTPException(409, "Item Name already exists")
        payload = self.writable({**data, "name": name})
        payload.setdefault("isActive", True)
        item = InventoryItem(**payload)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        out = self.serialize(item)
        out["isLowStock"] = _low_stock(item.quantity, item.alertQuantity)
        return ok(out, "Inventory item added successfully")

    def edit(self, item_id: int, data: dict) -> dict:
        item = self.db.get(InventoryItem, item_id)
        if not item:
            raise HTTPException(404, "Invalid item id")
        fields = self.writable(data)
        if fields.get("name"):
            dup = (
                self.db.query(InventoryItem)
                .filter(
                    func.lower(InventoryItem.name) == fields["name"].strip().lower(),
                    InventoryItem.id != item_id,
                )
                .first()
            )
            if dup:
                raise HTTPException(409, "Item Name already exists")
        for k, v in fields.items():
            setattr(item, k, v)
        self.db.commit()
        self.db.refresh(item)
        return ok(self.serialize(item), "Inventory item updated successfully")

    def toggle(self, item_id: int) -> dict:
        item = self.db.get(InventoryItem, item_id)
        if not item:
            raise HTTPException(404, "Invalid item id")
        item.isActive = not bool(item.isActive)
        self.db.commit()
        message = "Activated" if item.isActive else "De-Activated"
        return ok({"id": item_id, "isActive": item.isActive}, f"Item {message}")

    def list(self, q) -> dict:
        query = self.db.query(InventoryItem)
        if q.isActive is not None:
            query = query.filter(InventoryItem.isActive.is_(q.isActive))
        if q.department is not None:
            query = query.filter(InventoryItem.department == q.department)
        if q.lowStock:  # filter in SQL so pagination + total stay correct
            query = query.filter(
                InventoryItem.quantity.isnot(None),
                InventoryItem.alertQuantity.isnot(None),
                InventoryItem.quantity <= InventoryItem.alertQuantity,
            )
        if q.search and q.search.strip():
            term = f"%{q.search.strip().lower()}%"
            query = query.filter(
                or_(InventoryItem.name.ilike(term), InventoryItem.category.ilike(term))
            )
        query = query.order_by(InventoryItem.createdAt.desc())
        page, limit = q.page or 1, q.limit or 10
        total = query.count()
        rows = query.offset((page - 1) * limit).limit(limit).all()
        docs = []
        for item in rows:
            d = self.serialize(item)
            d["isLowStock"] = _low_stock(item.quantity, item.alertQuantity)
            docs.append(d)
        return ok(paginate(docs, total, page, limit), "success")

    def lot_numbers(self, item_id: int) -> dict:
        rows = (
            self.db.query(InventoryQuantity)
            .filter(InventoryQuantity.itemId == item_id, InventoryQuantity.isRemoved.isnot(True))
            .all()
        )
        lots = sorted({r.lotNumber for r in rows if r.lotNumber})
        return ok(lots, "Lot numbers")


class SubItemController(BaseController):
    model = InventorySubItem
    name = "Inventory sub-item"

    def add(self, data: dict) -> dict:
        name = (data.get("name") or "").strip()
        item_id = data.get("inventoryItemId")
        if not name:
            raise HTTPException(400, "name is required")
        if (
            self.db.query(InventorySubItem)
            .filter(
                InventorySubItem.inventoryItemId == item_id,
                func.lower(InventorySubItem.name) == name.lower(),
            )
            .first()
        ):
            raise HTTPException(409, "Sub Item Name already exists")
        sub = InventorySubItem(**self.writable({**data, "name": name}))
        self.db.add(sub)
        self.db.commit()
        self.db.refresh(sub)
        return ok(self.serialize(sub), "Sub item added successfully")

    def list_by_item(self, item_id: int) -> dict:
        rows = (
            self.db.query(InventorySubItem)
            .filter(InventorySubItem.inventoryItemId == item_id)
            .all()
        )
        return ok([self.serialize(r) for r in rows], "Sub item list")


class QuantityController(BaseController):
    model = InventoryQuantity
    name = "Inventory quantity"

    def list_by_item(self, item_id: int) -> dict:
        rows = (
            self.db.query(InventoryQuantity)
            .filter(InventoryQuantity.itemId == item_id, InventoryQuantity.isRemoved.isnot(True))
            .all()
        )
        return ok([self.serialize(r) for r in rows], "Quantity list")


class ProductImageController(BaseController):
    model = ProductImage
    name = "Product image"


class QrCodeController(BaseController):
    model = QrCode
    name = "QR code"
    search_fields = ("code",)


class BarcodeController(BaseController):
    model = Barcode
    name = "Barcode"
    search_fields = ("barcode",)


class BarcodeSessionController(BaseController):
    model = BarcodeSession
    name = "Barcode session"


class StaticDataController(BaseController):
    model = InventoryStaticData
    name = "Inventory static data"
    search_fields = ("title",)
