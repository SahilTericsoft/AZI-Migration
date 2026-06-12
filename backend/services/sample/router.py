"""Sample router (PHI) — protected + audited."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.deps import require_user_id
from services.sample import controller as c
from services.sample import schemas as s

router = APIRouter(prefix="/sample")
SMP = ["sample: samples"]


@router.post("/samples", tags=SMP)
def add_sample(
    body: s.SampleCreate, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.SampleController(db, actor_id=actor).add(body.model_dump(exclude_unset=True))


@router.post("/samples/list", tags=SMP)
def list_samples(
    body: s.SampleListQuery, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.SampleController(db, actor_id=actor).list(body)


@router.get("/samples/by-order/{order_id}", tags=SMP)
def samples_by_order(
    order_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.SampleController(db, actor_id=actor).list_by_order(order_id)


@router.put("/samples/{sample_id}/accession", tags=SMP)
def accession_sample(
    sample_id: int,
    body: s.AccessionIn,
    db: Session = Depends(get_db),
    actor: int = Depends(require_user_id),
):
    return c.SampleController(db, actor_id=actor).accession(
        sample_id, body.accessionedBy, status=body.status, lab_id=body.accessionedLabId
    )


@router.get("/samples/{sample_id}", tags=SMP)
def view_sample(
    sample_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.SampleController(db, actor_id=actor).view(sample_id)


@router.put("/samples/{sample_id}", tags=SMP)
def edit_sample(
    sample_id: int,
    body: s.SampleEdit,
    db: Session = Depends(get_db),
    actor: int = Depends(require_user_id),
):
    return c.SampleController(db, actor_id=actor).edit(
        sample_id, body.model_dump(exclude_unset=True)
    )


@router.delete("/samples/{sample_id}", tags=SMP)
def delete_sample(
    sample_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.SampleController(db, actor_id=actor).delete(sample_id)
