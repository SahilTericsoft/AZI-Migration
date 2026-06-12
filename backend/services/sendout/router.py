"""Sendout router (PHI) — protected + audited."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.api import ListIn
from core.database import get_db
from core.deps import require_user_id
from services.sendout import controller as c
from services.sendout import schemas as s

router = APIRouter(prefix="/sendout", dependencies=[Depends(require_user_id)])
TAG = ["sendout"]


@router.post("/batches", tags=TAG)
def add_batch(
    body: s.SendoutBatchCreate, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.SendoutBatchController(db, actor_id=actor).add(body.model_dump(exclude_unset=True))


@router.post("/batches/list", tags=TAG)
def list_batches(body: ListIn, db: Session = Depends(get_db)):
    return c.SendoutBatchController(db).list(body)


@router.get("/batches/by-lab/{lab_id}", tags=TAG)
def batches_by_lab(lab_id: int, db: Session = Depends(get_db)):
    return c.SendoutBatchController(db).list_by_lab(lab_id)


@router.get("/batches/{batch_id}", tags=TAG)
def get_batch(batch_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)):
    return c.SendoutBatchController(db, actor_id=actor).get(batch_id)


@router.put("/batches/{batch_id}", tags=TAG)
def edit_batch(
    batch_id: int,
    body: s.SendoutBatchUpdate,
    db: Session = Depends(get_db),
    actor: int = Depends(require_user_id),
):
    return c.SendoutBatchController(db, actor_id=actor).update(
        batch_id, body.model_dump(exclude_unset=True)
    )
