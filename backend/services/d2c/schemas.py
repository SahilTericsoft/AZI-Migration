"""Request schemas for the D2C service."""

from typing import Any

from pydantic import BaseModel

from core.api import MutationBody


class SignUpIn(MutationBody):
    emailId: str
    password: str
    firstName: str | None = None
    lastName: str | None = None


class LoginIn(BaseModel):
    emailId: str
    password: str


class ForgotPasswordIn(BaseModel):
    emailId: str
    newPassword: str


class CustomerEdit(MutationBody):
    pass


class AddressCreate(MutationBody):
    customerId: int


class AddressEdit(MutationBody):
    pass


class CartCreate(MutationBody):
    pass


class PlaceOrderIn(MutationBody):
    customerId: int
    products: list[dict[str, Any]]  # [{productId, quantity, productDetails:{price}}]


class OrderEdit(MutationBody):
    pass
