"""Inventory router — explicit routes wired to the controllers."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.api import ListIn
from core.database import get_db
from services.inventory import controller as c
from services.inventory import schemas as s

router = APIRouter(prefix="/inventory")
TAG = ["inventory"]


# --------------------------------------------------------------------- items
@router.post("/items", tags=TAG)
def add_item(body: s.ItemCreate, db: Session = Depends(get_db)):
    return c.ItemController(db).add(body.model_dump(exclude_unset=True))


@router.post("/items/list", tags=TAG)
def list_items(body: s.InventoryListQuery, db: Session = Depends(get_db)):
    return c.ItemController(db).list(body)


@router.get("/items/{item_id}", tags=TAG)
def get_item(item_id: int, db: Session = Depends(get_db)):
    return c.ItemController(db).get(item_id)


@router.put("/items/{item_id}", tags=TAG)
def edit_item(item_id: int, body: s.ItemEdit, db: Session = Depends(get_db)):
    return c.ItemController(db).edit(item_id, body.model_dump(exclude_unset=True))


@router.put("/items/{item_id}/toggle", tags=TAG)
def toggle_item(item_id: int, db: Session = Depends(get_db)):
    return c.ItemController(db).toggle(item_id)


@router.get("/items/{item_id}/lot-numbers", tags=TAG)
def item_lot_numbers(item_id: int, db: Session = Depends(get_db)):
    return c.ItemController(db).lot_numbers(item_id)


@router.get("/items/{item_id}/sub-items", tags=TAG)
def item_sub_items(item_id: int, db: Session = Depends(get_db)):
    return c.SubItemController(db).list_by_item(item_id)


@router.get("/items/{item_id}/quantities", tags=TAG)
def item_quantities(item_id: int, db: Session = Depends(get_db)):
    return c.QuantityController(db).list_by_item(item_id)


@router.delete("/items/{item_id}", tags=TAG)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    return c.ItemController(db).delete(item_id)


# ------------------------------------------------------------------ sub-items
@router.post("/sub-items", tags=TAG)
def add_sub_item(body: s.SubItemCreate, db: Session = Depends(get_db)):
    return c.SubItemController(db).add(body.model_dump(exclude_unset=True))


@router.delete("/sub-items/{sub_id}", tags=TAG)
def delete_sub_item(sub_id: int, db: Session = Depends(get_db)):
    return c.SubItemController(db).delete(sub_id)


# ----------------------------------------------------------------- quantities
@router.post("/quantities", tags=TAG)
def add_quantity(body: s.QuantityCreate, db: Session = Depends(get_db)):
    return c.QuantityController(db).create(body.model_dump(exclude_unset=True))


@router.put("/quantities/{q_id}", tags=TAG)
def edit_quantity(q_id: int, body: s.QuantityEdit, db: Session = Depends(get_db)):
    return c.QuantityController(db).update(q_id, body.model_dump(exclude_unset=True))


# -------------------------------------------------------------------- products
@router.post("/products", tags=TAG)
def add_product(body: s.ProductCreate, db: Session = Depends(get_db)):
    return c.ProductController(db).add(body.model_dump(exclude_unset=True))


@router.post("/products/list", tags=TAG)
def list_products(body: ListIn, db: Session = Depends(get_db)):
    return c.ProductController(db).list(body)


@router.get("/products/{product_id}", tags=TAG)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return c.ProductController(db).get(product_id)


@router.put("/products/{product_id}", tags=TAG)
def edit_product(product_id: int, body: s.ProductEdit, db: Session = Depends(get_db)):
    return c.ProductController(db).update(product_id, body.model_dump(exclude_unset=True))


@router.delete("/products/{product_id}", tags=TAG)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    return c.ProductController(db).delete(product_id)


# ----------------------------------------------- barcodes / qr / static data
def _simple(prefix, controller_cls, create_schema):
    @router.post(f"/{prefix}", tags=TAG, name=f"add_{prefix}")
    def add(body: create_schema, db: Session = Depends(get_db)):
        return controller_cls(db).create(body.model_dump(exclude_unset=True))

    @router.post(f"/{prefix}/list", tags=TAG, name=f"list_{prefix}")
    def listing(body: ListIn, db: Session = Depends(get_db)):
        return controller_cls(db).list(body)

    @router.get(f"/{prefix}/{{row_id}}", tags=TAG, name=f"get_{prefix}")
    def get(row_id: int, db: Session = Depends(get_db)):
        return controller_cls(db).get(row_id)

    @router.put(f"/{prefix}/{{row_id}}", tags=TAG, name=f"edit_{prefix}")
    def edit(row_id: int, body: s.SimpleCreate, db: Session = Depends(get_db)):
        return controller_cls(db).update(row_id, body.model_dump(exclude_unset=True))

    @router.delete(f"/{prefix}/{{row_id}}", tags=TAG, name=f"delete_{prefix}")
    def delete(row_id: int, db: Session = Depends(get_db)):
        return controller_cls(db).delete(row_id)


_simple("barcodes", c.BarcodeController, s.SimpleCreate)
_simple("qr-codes", c.QrCodeController, s.SimpleCreate)
_simple("barcode-sessions", c.BarcodeSessionController, s.SimpleCreate)
_simple("product-images", c.ProductImageController, s.SimpleCreate)
_simple("static-data", c.StaticDataController, s.SimpleCreate)
