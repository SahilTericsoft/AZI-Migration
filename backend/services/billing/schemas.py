"""Request schemas for the Billing reference service."""

from core.api import MutationBody


class InsurerCreate(MutationBody):
    title: str


class InsurerUpdate(MutationBody):
    pass


class ClearingHouseCreate(MutationBody):
    clearingHouse: str


class ClearingHouseUpdate(MutationBody):
    pass


class ClearingHouseInsuranceCreate(MutationBody):
    clearingHouseId: int


class ClearingHouseInsuranceUpdate(MutationBody):
    pass
