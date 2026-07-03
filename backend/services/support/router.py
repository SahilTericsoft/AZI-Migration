"""Support router — Support Center (help sections) + Resources (documents)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.api import ListIn
from core.database import get_db
from services.support import controller as c
from services.support import schemas as s

router = APIRouter(prefix="/support")
TAG = ["support"]

# Legacy-compatible alias so the client can call the exact path the existing UI
# uses (admin-console `helpSection` service). Same data, original endpoint name.
legacy_router = APIRouter(prefix="/helpSection", tags=TAG)


@legacy_router.get("/getHelpSectionsListLiteClient")
def get_help_sections_list_lite_client(db: Session = Depends(get_db)):
    return c.HelpSectionController(db).listing()


# ------------------------------------------------------ Resources (documents)
@router.post("/documents", tags=TAG)
def add_document(body: s.DocumentCreate, db: Session = Depends(get_db)):
    return c.DocumentController(db).add(body.model_dump(exclude_unset=True))


@router.post("/documents/list", tags=TAG)
def list_documents(body: ListIn, db: Session = Depends(get_db)):
    return c.DocumentController(db).list(body)


@router.delete("/documents/{doc_id}", tags=TAG)
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    return c.DocumentController(db).delete(doc_id)


# ------------------------------------------------ Support Center (help center)
@router.get("/help-sections", tags=TAG)
def list_help_sections(db: Session = Depends(get_db)):
    return c.HelpSectionController(db).listing()


@router.post("/help-sections", tags=TAG)
def add_help_section(body: s.HelpSectionCreate, db: Session = Depends(get_db)):
    return c.HelpSectionController(db).add(body.model_dump(exclude_unset=True))
