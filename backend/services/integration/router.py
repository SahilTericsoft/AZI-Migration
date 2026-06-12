"""Integration router — AdvancedMD tokens (protected) + OCR config."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.api import ListIn
from core.database import get_db
from core.deps import require_user_id
from services.integration import controller as c
from services.integration import schemas as s

router = APIRouter(prefix="/integration")
TAG = ["integration"]


@router.post("/advancedmd-tokens", tags=TAG)
def upsert_amd_token(
    body: s.AdvancedMDTokenCreate,
    db: Session = Depends(get_db),
    actor: int = Depends(require_user_id),
):
    return c.AdvancedMDTokenController(db).upsert(body.model_dump(exclude_unset=True))


@router.post("/advancedmd-tokens/list", tags=TAG)
def list_amd_tokens(
    body: ListIn, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.AdvancedMDTokenController(db).list(body)


@router.get("/advancedmd-tokens/{token_id}", tags=TAG)
def get_amd_token(
    token_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.AdvancedMDTokenController(db).get(token_id)


def _crud(prefix, controller_cls, create_schema, edit_schema):
    @router.post(f"/{prefix}", tags=TAG, name=f"add_{prefix}")
    def add(body: create_schema, db: Session = Depends(get_db)):
        return controller_cls(db).create(body.model_dump(exclude_unset=True))

    @router.post(f"/{prefix}/list", tags=TAG, name=f"list_{prefix}")
    def listing(body: ListIn, db: Session = Depends(get_db)):
        return controller_cls(db).list(body)

    @router.get(f"/{prefix}/{{row_id}}", tags=TAG, name=f"get_{prefix}")
    def get(row_id: int, db: Session = Depends(get_db)):
        return controller_cls(db).get(row_id)

    @router.put(f"/{prefix}/{{row_id}}", tags=TAG, name=f"edit_{prefix}")
    def edit(row_id: int, body: edit_schema, db: Session = Depends(get_db)):
        return controller_cls(db).update(row_id, body.model_dump(exclude_unset=True))


_crud("ocr-companies", c.OcrCompanyController, s.OcrCompanyCreate, s.OcrCompanyUpdate)
_crud("ocr-settings", c.OcrSettingController, s.OcrSettingCreate, s.OcrSettingUpdate)
