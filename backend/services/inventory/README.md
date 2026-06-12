# Inventory service

Consolidates **GkInventoryService** + **GkLabInventoryService**. Mounted at
`/inventory`.

## Files
`models.py` (Product, ProductImage, QrCode, Barcode, BarcodeSession,
InventoryItem, InventorySubItem, InventoryQuantity, InventoryStaticData) ·
`schemas.py` · `controller.py` · `router.py`

## Entities & endpoints
Standard CRUD on `/inventory/{products|product-images|qr-codes|barcodes|
barcode-sessions|items|sub-items|quantities|static-data}`.

## Domain logic
- **ProductController** soft-deletes (Products has `isDeleted`) and defaults
  active/not-deleted on create.
- Legacy reserved column `InventoryQuantities.order` is modelled as `orderInfo`.

## Tests
`tests/test_remaining_services.py` — products, items, product soft-delete.
