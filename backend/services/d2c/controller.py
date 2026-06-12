"""Controllers for the D2C service (PHI).

Ported from GkD2CService (AuthController + CustomerController). Real logic:
  * customer sign-up (email dedupe, bcrypt password), login (verify), forgot-
    password (re-hash)
  * addresses with single-default enforcement
  * kit orders priced from product price x quantity, `orderCode` = `D2C{id}`
Customer/address/order access is audited; the password is never returned.
"""

from __future__ import annotations

from fastapi import HTTPException

from core.api import ok
from core.controller import BaseController
from core.security import hash_password, verify_password
from services.d2c.models import (
    CUSTOMER_SENSITIVE,
    Customer,
    CustomerAddress,
    CustomerCart,
    D2COrder,
)


class CustomerController(BaseController):
    model = Customer
    name = "Customer"
    sensitive = CUSTOMER_SENSITIVE
    search_fields = ("firstName", "lastName", "emailId")
    audit_entity = "Customer"

    def sign_up(self, data: dict) -> dict:
        email = (data.get("emailId") or "").strip().lower()
        if not email or not data.get("password"):
            raise HTTPException(400, "emailId and password are required")
        if self.db.query(Customer).filter(Customer.emailId == email).first():
            raise HTTPException(409, "Email already in use")
        payload = self.writable({**data, "emailId": email})
        payload["password"] = hash_password(data["password"])
        payload.setdefault("isActive", True)
        customer = Customer(**payload)
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        self.audit("create", customer.id)
        return ok(self.serialize(customer), "Customer registered successfully")

    def login(self, email: str, password: str) -> dict:
        customer = self.db.query(Customer).filter(Customer.emailId == email.strip().lower()).first()
        if not customer or not verify_password(password, customer.password):
            raise HTTPException(403, "Invalid login credentials")
        if not customer.isActive:
            raise HTTPException(403, "Customer account is inactive")
        self.audit("view", customer.id)
        return ok(self.serialize(customer), "Login Successful")

    def forgot_password(self, email: str, new_password: str) -> dict:
        customer = self.db.query(Customer).filter(Customer.emailId == email.strip().lower()).first()
        if not customer:
            raise HTTPException(404, "Customer not found")
        customer.password = hash_password(new_password)
        self.db.commit()
        self.audit("update", customer.id)
        return ok({}, "Password updated successfully")


class CustomerAddressController(BaseController):
    model = CustomerAddress
    name = "Customer address"
    audit_entity = "CustomerAddress"

    def add(self, data: dict) -> dict:
        address = CustomerAddress(**self.writable(data))
        self.db.add(address)
        self.db.commit()
        self.db.refresh(address)
        if address.isDefault:
            self._unset_other_defaults(address.customerId, address.id)
        self.audit("create", address.id)
        return ok(self.serialize(address), "Address added successfully")

    def make_default(self, address_id: int) -> dict:
        address = self.db.get(CustomerAddress, address_id)
        if not address:
            raise HTTPException(404, "Invalid address id")
        address.isDefault = True
        self._unset_other_defaults(address.customerId, address_id)
        self.audit("update", address_id)
        return ok(self.serialize(address), "Default address set")

    def _unset_other_defaults(self, customer_id: int, keep_id: int) -> None:
        self.db.query(CustomerAddress).filter(
            CustomerAddress.customerId == customer_id,
            CustomerAddress.id != keep_id,
        ).update({"isDefault": False})
        self.db.commit()

    def list_by_customer(self, customer_id: int) -> dict:
        rows = (
            self.db.query(CustomerAddress).filter(CustomerAddress.customerId == customer_id).all()
        )
        return ok([self.serialize(r) for r in rows], "Address list")


class CustomerCartController(BaseController):
    model = CustomerCart
    name = "Customer cart"


class D2COrderController(BaseController):
    model = D2COrder
    name = "D2C order"
    search_fields = ("orderCode",)
    audit_entity = "D2COrder"

    def place_order(self, data: dict) -> dict:
        items, total = [], 0.0
        for product in data.get("products", []):
            qty = float(product.get("quantity") or 0)
            price = float((product.get("productDetails") or {}).get("price") or 0)
            line_total = price * qty
            total += line_total
            items.append(
                {
                    "productId": product.get("productId"),
                    "quantity": qty,
                    "price": price,
                    "totalPrice": line_total,
                }
            )

        payload = self.writable(data)
        payload["summary"] = {"products": items, "total": total}
        payload.setdefault("paymentStatus", "pending")
        order = D2COrder(**payload)
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        order.orderCode = f"D2C{order.id}"
        self.db.commit()
        self.audit("create", order.id)
        return ok(self.serialize(order), "Order placed successfully")

    def list_by_customer(self, customer_id: int) -> dict:
        rows = (
            self.db.query(D2COrder)
            .filter(D2COrder.customerId == customer_id)
            .order_by(D2COrder.createdAt.desc())
            .all()
        )
        return ok([self.serialize(r) for r in rows], "Order list")
