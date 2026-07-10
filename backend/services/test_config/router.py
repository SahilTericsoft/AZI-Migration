"""Test Configuration router — explicit routes wired to the controllers.

Surfaces the real legacy endpoints: add, list (rich filters), list-lite, view,
edit, draft-aware toggle, and code-duplicate check.
"""

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm import Session

from core import storage
from core.api import ok
from core.database import get_db
from services.test_config import controller as c
from services.test_config import schemas as s
from services.test_config.models import Test

router = APIRouter(prefix="/test-config")
PANEL = ["test-config: panels"]
TEST = ["test-config: tests"]
BIO = ["test-config: biomarkers"]
CPT = ["test-config: cpt-codes"]
ICD = ["test-config: icd-codes"]
CONFIG = ["test-config: biomarker configurations"]


# ----------------------------------------------------------------- Panels
@router.post("/panels", tags=PANEL)
def add_panel(body: s.PanelCreate, db: Session = Depends(get_db)):
    return c.PanelController(db).add(body.model_dump(exclude_unset=True))


@router.post("/panels/list", tags=PANEL)
def list_panels(body: s.CatalogListQuery, db: Session = Depends(get_db)):
    return c.PanelController(db).list(body)


@router.post("/panels/list-lite", tags=PANEL)
def list_panels_lite(body: s.ListLiteQuery, db: Session = Depends(get_db)):
    return c.PanelController(db).list_lite(body)


@router.post("/panels/check-code", tags=PANEL)
def check_panel_code(body: s.CheckCodeIn, db: Session = Depends(get_db)):
    return c.PanelController(db).check_code(body.code)


@router.get("/panels/{panel_id}", tags=PANEL)
def view_panel(
    panel_id: int, isActive: bool | None = Query(default=None), db: Session = Depends(get_db)
):
    return c.PanelController(db).view(panel_id, is_active=isActive)


@router.put("/panels/{panel_id}", tags=PANEL)
def edit_panel(panel_id: int, body: s.PanelEdit, db: Session = Depends(get_db)):
    return c.PanelController(db).edit(panel_id, body.model_dump(exclude_unset=True))


@router.put("/panels/{panel_id}/toggle", tags=PANEL)
def toggle_panel(panel_id: int, db: Session = Depends(get_db)):
    return c.PanelController(db).toggle(panel_id)


@router.delete("/panels/{panel_id}", tags=PANEL)
def delete_panel(panel_id: int, db: Session = Depends(get_db)):
    return c.PanelController(db).delete(panel_id)


# ------------------------------------------------------------------ Tests
@router.post("/tests", tags=TEST)
def add_test(body: s.TestCreate, db: Session = Depends(get_db)):
    return c.TestController(db).add(body.model_dump(exclude_unset=True))


@router.post("/tests/list", tags=TEST)
def list_tests(body: s.CatalogListQuery, db: Session = Depends(get_db)):
    return c.TestController(db).list(body)


@router.post("/tests/list-lite", tags=TEST)
def list_tests_lite(body: s.ListLiteQuery, db: Session = Depends(get_db)):
    return c.TestController(db).list_lite(body)


@router.post("/tests/check-code", tags=TEST)
def check_test_code(body: s.CheckCodeIn, db: Session = Depends(get_db)):
    return c.TestController(db).check_code(body.code)


@router.post("/tests/layout-preview", tags=TEST)
def preview_test_layout(body: s.TestLayoutPreview, db: Session = Depends(get_db)):
    """Render the configured report layout to a sample PDF (legacy preview)."""
    pdf = c.TestController(db).preview_layout(body.model_dump(exclude_unset=True))
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": 'inline; filename="report-preview.pdf"'},
    )


@router.get("/tests/{test_id}", tags=TEST)
def view_test(test_id: int, db: Session = Depends(get_db)):
    return c.TestController(db).view(test_id)


@router.put("/tests/{test_id}", tags=TEST)
def edit_test(test_id: int, body: s.TestEdit, db: Session = Depends(get_db)):
    return c.TestController(db).edit(test_id, body.model_dump(exclude_unset=True))


@router.put("/tests/{test_id}/toggle", tags=TEST)
def toggle_test(test_id: int, db: Session = Depends(get_db)):
    return c.TestController(db).toggle(test_id)


@router.delete("/tests/{test_id}", tags=TEST)
def delete_test(test_id: int, db: Session = Depends(get_db)):
    return c.TestController(db).delete(test_id)


# ------------------------------------------------ Test (Panel) attachments
@router.post("/tests/{test_id}/attachments", tags=TEST)
async def upload_test_attachment(
    test_id: int,
    attachmentName: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a document to Azure Blob and record it on the test.

    Returns 503 until `AZURE_STORAGE_CONNECTION_STRING` is configured.
    """
    test = db.get(Test, test_id)
    if not test:
        raise HTTPException(404, "Test not found")
    data = await file.read()
    url = storage.upload_attachment(
        data, file.filename or "attachment", file.content_type, prefix=str(test_id)
    )
    record = {
        "attachmentName": attachmentName,
        "secureUrl": url,
        "mimeType": file.content_type,
        "size": len(data),
    }
    test.attachments = [*(test.attachments or []), record]
    flag_modified(test, "attachments")
    db.commit()
    return ok(record, "Attachment uploaded")


@router.delete("/tests/{test_id}/attachments/{index}", tags=TEST)
def delete_test_attachment(test_id: int, index: int, db: Session = Depends(get_db)):
    test = db.get(Test, test_id)
    if not test:
        raise HTTPException(404, "Test not found")
    items = list(test.attachments or [])
    if index < 0 or index >= len(items):
        raise HTTPException(404, "Attachment not found")
    items.pop(index)
    test.attachments = items
    flag_modified(test, "attachments")
    db.commit()
    return ok({}, "Attachment removed")


# ------------------------------------------------------------- Biomarkers
@router.post("/biomarkers", tags=BIO)
def add_biomarker(body: s.BiomarkerCreate, db: Session = Depends(get_db)):
    return c.BiomarkerController(db).add(body.model_dump(exclude_unset=True))


@router.post("/biomarkers/list", tags=BIO)
def list_biomarkers(body: s.CatalogListQuery, db: Session = Depends(get_db)):
    return c.BiomarkerController(db).list(body)


@router.post("/biomarkers/list-lite", tags=BIO)
def list_biomarkers_lite(body: s.ListLiteQuery, db: Session = Depends(get_db)):
    return c.BiomarkerController(db).list_lite(body)


@router.post("/biomarkers/check-code", tags=BIO)
def check_biomarker_code(body: s.CheckCodeIn, db: Session = Depends(get_db)):
    return c.BiomarkerController(db).check_code(body.code)


@router.get("/biomarkers/{biomarker_id}", tags=BIO)
def view_biomarker(biomarker_id: int, db: Session = Depends(get_db)):
    return c.BiomarkerController(db).get(biomarker_id)


@router.put("/biomarkers/{biomarker_id}", tags=BIO)
def edit_biomarker(biomarker_id: int, body: s.BiomarkerEdit, db: Session = Depends(get_db)):
    return c.BiomarkerController(db).edit(biomarker_id, body.model_dump(exclude_unset=True))


@router.put("/biomarkers/{biomarker_id}/toggle", tags=BIO)
def toggle_biomarker(biomarker_id: int, db: Session = Depends(get_db)):
    return c.BiomarkerController(db).toggle(biomarker_id)


@router.delete("/biomarkers/{biomarker_id}", tags=BIO)
def delete_biomarker(biomarker_id: int, db: Session = Depends(get_db)):
    return c.BiomarkerController(db).delete(biomarker_id)


# ----------------------------------------- Biomarker report configurations
@router.get("/biomarkers/{biomarker_id}/configurations", tags=CONFIG)
def list_biomarker_configs(biomarker_id: int, db: Session = Depends(get_db)):
    return c.BiomarkerReportConfigController(db).list_for_biomarker(biomarker_id)


@router.post("/biomarkers/{biomarker_id}/configurations", tags=CONFIG)
def add_biomarker_config(
    biomarker_id: int, body: s.BiomarkerConfigCreate, db: Session = Depends(get_db)
):
    return c.BiomarkerReportConfigController(db).add_for_biomarker(
        biomarker_id, body.model_dump(exclude_unset=True)
    )


@router.put("/configurations/{config_id}", tags=CONFIG)
def edit_biomarker_config(
    config_id: int, body: s.BiomarkerConfigEdit, db: Session = Depends(get_db)
):
    return c.BiomarkerReportConfigController(db).edit(
        config_id, body.model_dump(exclude_unset=True)
    )


@router.delete("/configurations/{config_id}", tags=CONFIG)
def delete_biomarker_config(config_id: int, db: Session = Depends(get_db)):
    return c.BiomarkerReportConfigController(db).remove(config_id)


# ---------------------------------------------------------- CPT / ICD codes
@router.post("/cpt-codes", tags=CPT)
def add_cpt(body: s.CptCodeCreate, db: Session = Depends(get_db)):
    return c.CptCodeController(db).add(body.model_dump(exclude_unset=True))


@router.post("/cpt-codes/list", tags=CPT)
def list_cpt(body: s.CatalogListQuery, db: Session = Depends(get_db)):
    return c.CptCodeController(db).list(body)


@router.get("/cpt-codes/{cpt_id}", tags=CPT)
def view_cpt(cpt_id: int, db: Session = Depends(get_db)):
    return c.CptCodeController(db).get(cpt_id)


@router.put("/cpt-codes/{cpt_id}", tags=CPT)
def edit_cpt(cpt_id: int, body: s.CptCodeEdit, db: Session = Depends(get_db)):
    return c.CptCodeController(db).update(cpt_id, body.model_dump(exclude_unset=True))


@router.delete("/cpt-codes/{cpt_id}", tags=CPT)
def delete_cpt(cpt_id: int, db: Session = Depends(get_db)):
    return c.CptCodeController(db).delete(cpt_id)


@router.post("/icd-codes", tags=ICD)
def add_icd(body: s.IcdCodeCreate, db: Session = Depends(get_db)):
    return c.IcdCodeController(db).add(body.model_dump(exclude_unset=True))


@router.post("/icd-codes/list", tags=ICD)
def list_icd(body: s.CatalogListQuery, db: Session = Depends(get_db)):
    return c.IcdCodeController(db).list(body)


@router.get("/icd-codes/{icd_id}", tags=ICD)
def view_icd(icd_id: int, db: Session = Depends(get_db)):
    return c.IcdCodeController(db).get(icd_id)


@router.put("/icd-codes/{icd_id}", tags=ICD)
def edit_icd(icd_id: int, body: s.IcdCodeEdit, db: Session = Depends(get_db)):
    return c.IcdCodeController(db).update(icd_id, body.model_dump(exclude_unset=True))


@router.delete("/icd-codes/{icd_id}", tags=ICD)
def delete_icd(icd_id: int, db: Session = Depends(get_db)):
    return c.IcdCodeController(db).delete(icd_id)
