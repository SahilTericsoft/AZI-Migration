"""Result router (PHI) — protected + audited."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.api import ListIn
from core.database import get_db
from core.deps import require_user_id
from services.result import controller as c
from services.result import schemas as s

router = APIRouter(prefix="/result", dependencies=[Depends(require_user_id)])
TAG = ["result"]


@router.post("/samples", tags=TAG)
def add_sample(
    body: s.ResultSampleCreate, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.ResultSampleController(db, actor_id=actor).create(body.model_dump(exclude_unset=True))


@router.post("/samples/list", tags=TAG)
def list_samples(body: ListIn, db: Session = Depends(get_db)):
    return c.ResultSampleController(db).list(body)


@router.get("/samples/by-session/{session_id}", tags=TAG)
def samples_by_session(session_id: int, db: Session = Depends(get_db)):
    return c.ResultSampleController(db).list_by_session(session_id)


@router.get("/samples/by-order/{order_id}", tags=TAG)
def samples_by_order(order_id: int, db: Session = Depends(get_db)):
    return c.ResultSampleController(db).list_by_order(order_id)


@router.get("/samples/{sample_id}", tags=TAG)
def get_sample(
    sample_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.ResultSampleController(db, actor_id=actor).get(sample_id)


@router.put("/samples/{sample_id}", tags=TAG)
def edit_sample(
    sample_id: int,
    body: s.ResultSampleUpdate,
    db: Session = Depends(get_db),
    actor: int = Depends(require_user_id),
):
    return c.ResultSampleController(db, actor_id=actor).update(
        sample_id, body.model_dump(exclude_unset=True)
    )


@router.post("/controls", tags=TAG)
def add_control(
    body: s.ResultControlCreate,
    db: Session = Depends(get_db),
    actor: int = Depends(require_user_id),
):
    return c.ResultControlController(db, actor_id=actor).create(body.model_dump(exclude_unset=True))


@router.get("/controls/by-session/{session_id}", tags=TAG)
def controls_by_session(session_id: int, db: Session = Depends(get_db)):
    return c.ResultControlController(db).list_by_session(session_id)
