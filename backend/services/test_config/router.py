"""Test Configuration router — explicit routes wired to the controllers.

Surfaces the real legacy endpoints: add, list (rich filters), list-lite, view,
edit, draft-aware toggle, and code-duplicate check.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from services.test_config import controller as c
from services.test_config import schemas as s

router = APIRouter(prefix="/test-config")
PANEL = ["test-config: panels"]
TEST = ["test-config: tests"]
BIO = ["test-config: biomarkers"]
CPT = ["test-config: cpt-codes"]
ICD = ["test-config: icd-codes"]


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
