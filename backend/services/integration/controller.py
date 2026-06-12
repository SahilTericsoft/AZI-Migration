"""Controllers for the Integration service.

Real logic: AdvancedMD token upsert keyed by userName+officeKey (credentials
rotate in place); token masked. OCR config CRUD.
"""

from core.api import ok
from core.controller import BaseController
from services.integration.models import (
    ADVANCEDMD_SENSITIVE,
    AdvancedMDToken,
    OcrCompany,
    OcrSetting,
)


class AdvancedMDTokenController(BaseController):
    model = AdvancedMDToken
    name = "AdvancedMD token"
    sensitive = ADVANCEDMD_SENSITIVE
    search_fields = ("userName",)

    def upsert(self, data: dict) -> dict:
        row = (
            self.db.query(AdvancedMDToken)
            .filter(
                AdvancedMDToken.userName == data.get("userName"),
                AdvancedMDToken.officeKey == data.get("officeKey"),
            )
            .first()
        )
        if row:
            for key, value in self.writable(data).items():
                setattr(row, key, value)
            message = "AdvancedMD token updated"
        else:
            row = AdvancedMDToken(**self.writable(data))
            self.db.add(row)
            message = "AdvancedMD token created"
        self.db.commit()
        self.db.refresh(row)
        return ok(self.serialize(row), message)


class OcrCompanyController(BaseController):
    model = OcrCompany
    name = "OCR company"
    search_fields = ("companyName",)


class OcrSettingController(BaseController):
    model = OcrSetting
    name = "OCR setting"
    search_fields = ("title", "code")
