# Integration service

External-system credentials & config — **GkAdvancedMDService** + **GkOCRService**.
Mounted at `/integration`.

## Files
`models.py` (AdvancedMDToken, OcrCompany, OcrSetting) · `schemas.py` ·
`controller.py` · `router.py`

## Entities & endpoints
Standard CRUD on:
- `/integration/advancedmd-tokens` — **protected** (token masked)
- `/integration/ocr-companies` — config
- `/integration/ocr-settings` — config

## Tests
`tests/test_remaining_services.py` — OCR company CRUD, AdvancedMD token mask + auth.
