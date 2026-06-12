# D2C (Direct-to-Consumer) service (PHI)

Migrated from **GkD2CService**. Mounted at `/d2c`.

## Files
`models.py` (Customer, CustomerAddress, CustomerCart, D2COrder) · `schemas.py` ·
`controller.py` · `router.py`

## Entities & endpoints
Standard CRUD on:
- `/d2c/customers` — **PHI, protected + audited** (password masked)
- `/d2c/addresses` — **PHI, protected + audited**
- `/d2c/carts` — open
- `/d2c/orders` — **PHI, protected + audited**

## HIPAA
Customer/address/order endpoints require a bearer token and are audited;
customer `password` is never returned.

## Domain logic
- **CustomerController** defaults `isActive=true`; **D2COrderController**
  generates an order code (`D2C000001`).

## Tests
`tests/test_remaining_services.py` — customers (PHI + password mask + auth).
