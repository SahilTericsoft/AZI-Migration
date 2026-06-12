"""Request schemas for the Integration service."""

from core.api import MutationBody


class AdvancedMDTokenCreate(MutationBody):
    userName: str


class AdvancedMDTokenUpdate(MutationBody):
    pass


class OcrCompanyCreate(MutationBody):
    companyName: str


class OcrCompanyUpdate(MutationBody):
    pass


class OcrSettingCreate(MutationBody):
    title: str


class OcrSettingUpdate(MutationBody):
    pass
