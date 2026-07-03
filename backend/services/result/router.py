"""Result router (PHI) — protected + audited."""

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from core.api import ListIn
from core.database import get_db
from core.deps import require_user_id
from services.result import controller as c
from services.result import schemas as s

router = APIRouter(prefix="/result", dependencies=[Depends(require_user_id)])
TAG = ["result"]
SES = ["result: sessions"]


# ---------------------------------------------------------- result sessions
@router.post("/worklist-by-test-panel", tags=SES)
def worklist_by_test_panel(body: s.WorklistByTestPanelIn, db: Session = Depends(get_db)):
    return c.ResultController(db).worklist_by_test_panel(body.model_dump(exclude_unset=True))


@router.post("/manual-template", tags=SES)
def manual_template(body: s.ManualTemplateIn, db: Session = Depends(get_db)):
    return c.ResultController(db).manual_template(body.model_dump(exclude_unset=True))


@router.post("/manual-submit", tags=SES)
def manual_submit(
    body: s.ManualSubmitIn, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.ResultController(db, actor_id=actor).manual_submit(
        body.model_dump(exclude_unset=True), actor
    )


@router.post("/upload-runfile", tags=SES)
async def upload_runfile(
    file: UploadFile = File(...),
    worklistId: int | None = Form(None),
    cqCutoff: float | None = Form(None),
    db: Session = Depends(get_db),
    actor: int = Depends(require_user_id),
):
    content = await file.read()
    data = {"worklistId": worklistId, "cqCutoff": cqCutoff}
    return c.ResultController(db, actor_id=actor).upload_runfile(
        content, file.filename or "runfile.csv", data, actor
    )


@router.post("/sessions/list", tags=SES)
def list_sessions(body: s.ResultSessionListQuery, db: Session = Depends(get_db)):
    return c.ResultController(db).list_sessions(body)


@router.get("/sessions/{session_id}", tags=SES)
def session_detail(session_id: int, db: Session = Depends(get_db)):
    return c.ResultController(db).session_detail(session_id)


@router.get("/sessions/{session_id}/samples", tags=SES)
def session_samples(session_id: int, db: Session = Depends(get_db)):
    return c.ResultController(db).session_samples(session_id)


@router.get("/sessions/{session_id}/controls", tags=SES)
def session_controls(session_id: int, db: Session = Depends(get_db)):
    return c.ResultController(db).session_controls(session_id)


@router.put("/result-samples/{sample_id}", tags=SES)
def edit_result_sample(
    sample_id: int, body: s.SessionActionIn, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.ResultController(db, actor_id=actor).edit_sample(sample_id, body.model_dump(exclude_unset=True))


@router.put("/result-controls/{control_id}", tags=SES)
def edit_result_control(
    control_id: int, body: s.SessionActionIn, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.ResultController(db, actor_id=actor).edit_control(control_id, body.model_dump(exclude_unset=True))


@router.put("/sessions/{session_id}/recalculate-controls", tags=SES)
def recalculate_controls(
    session_id: int, body: s.SessionActionIn, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.ResultController(db, actor_id=actor).recalculate_controls(session_id, body.model_dump(exclude_unset=True))


@router.put("/sessions/{session_id}/reject-sample", tags=SES)
def reject_sample(
    session_id: int, body: s.SessionActionIn, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.ResultController(db, actor_id=actor).reject_sample(session_id, body.model_dump(exclude_unset=True))


@router.put("/sessions/{session_id}/mark-rerun", tags=SES)
def mark_rerun(
    session_id: int, body: s.SessionActionIn, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.ResultController(db, actor_id=actor).mark_rerun(session_id, body.model_dump(exclude_unset=True))


@router.put("/sessions/{session_id}/generate-report", tags=SES)
def generate_report(
    session_id: int, body: s.SessionActionIn, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.ResultController(db, actor_id=actor).generate_report(session_id, body.model_dump(exclude_unset=True))


@router.put("/sessions/{session_id}/discard", tags=SES)
def discard_session(session_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)):
    return c.ResultController(db, actor_id=actor).discard_session(session_id)


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
