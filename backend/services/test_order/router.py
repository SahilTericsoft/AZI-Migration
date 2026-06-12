"""Test Order router (PHI) — all entities protected + audited."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.deps import require_user_id
from services.test_order import controller as c
from services.test_order import schemas as s

router = APIRouter(prefix="/test-order")
ORD = ["test-order: orders"]
RES = ["test-order: results"]
GUA = ["test-order: guarantors"]
VIS = ["test-order: visits"]


# ------------------------------------------------------------------- orders
@router.post("/orders", tags=ORD)
def add_order(
    body: s.OrderCreate, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.OrderController(db, actor_id=actor).add(body.model_dump(exclude_unset=True))


@router.post("/orders/list", tags=ORD)
def list_orders(
    body: s.OrderListQuery, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.OrderController(db, actor_id=actor).list(body)


@router.get("/orders/{order_id}", tags=ORD)
def view_order(order_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)):
    return c.OrderController(db, actor_id=actor).view(order_id)


@router.put("/orders/{order_id}", tags=ORD)
def edit_order(
    order_id: int,
    body: s.OrderEdit,
    db: Session = Depends(get_db),
    actor: int = Depends(require_user_id),
):
    return c.OrderController(db, actor_id=actor).edit(order_id, body.model_dump(exclude_unset=True))


@router.delete("/orders/{order_id}", tags=ORD)
def delete_order(
    order_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.OrderController(db, actor_id=actor).delete(order_id)


# ------------------------------------------------------------------ results
@router.post("/order-results", tags=RES)
def add_result(
    body: s.OrderResultCreate, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.OrderResultController(db, actor_id=actor).create(body.model_dump(exclude_unset=True))


@router.get("/order-results/by-order/{order_id}", tags=RES)
def results_by_order(
    order_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.OrderResultController(db, actor_id=actor).list_by_order(order_id)


@router.get("/order-results/{result_id}", tags=RES)
def get_result(
    result_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.OrderResultController(db, actor_id=actor).get(result_id)


@router.put("/order-results/{result_id}", tags=RES)
def edit_result(
    result_id: int,
    body: s.OrderResultEdit,
    db: Session = Depends(get_db),
    actor: int = Depends(require_user_id),
):
    return c.OrderResultController(db, actor_id=actor).update(
        result_id, body.model_dump(exclude_unset=True)
    )


@router.delete("/order-results/{result_id}", tags=RES)
def delete_result(
    result_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.OrderResultController(db, actor_id=actor).delete(result_id)


# --------------------------------------------------------------- guarantors
@router.post("/guarantors", tags=GUA)
def add_guarantor(
    body: s.GuarantorCreate, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.GuarantorController(db, actor_id=actor).create(body.model_dump(exclude_unset=True))


@router.get("/guarantors/by-order/{order_id}", tags=GUA)
def guarantor_by_order(
    order_id: str, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.GuarantorController(db, actor_id=actor).get_by_order(order_id)


@router.get("/guarantors/{guarantor_id}", tags=GUA)
def get_guarantor(
    guarantor_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.GuarantorController(db, actor_id=actor).get(guarantor_id)


@router.put("/guarantors/{guarantor_id}", tags=GUA)
def edit_guarantor(
    guarantor_id: int,
    body: s.GuarantorEdit,
    db: Session = Depends(get_db),
    actor: int = Depends(require_user_id),
):
    return c.GuarantorController(db, actor_id=actor).update(
        guarantor_id, body.model_dump(exclude_unset=True)
    )


@router.delete("/guarantors/{guarantor_id}", tags=GUA)
def delete_guarantor(
    guarantor_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.GuarantorController(db, actor_id=actor).delete(guarantor_id)


# ------------------------------------------------------------ patient visits
@router.post("/patient-visits", tags=VIS)
def add_visit(
    body: s.PatientVisitCreate, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.PatientVisitController(db, actor_id=actor).create(body.model_dump(exclude_unset=True))


@router.get("/patient-visits/by-order/{order_id}", tags=VIS)
def visit_by_order(
    order_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.PatientVisitController(db, actor_id=actor).get_by_order(order_id)


@router.get("/patient-visits/{visit_id}", tags=VIS)
def get_visit(visit_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)):
    return c.PatientVisitController(db, actor_id=actor).get(visit_id)


@router.put("/patient-visits/{visit_id}", tags=VIS)
def edit_visit(
    visit_id: int,
    body: s.PatientVisitEdit,
    db: Session = Depends(get_db),
    actor: int = Depends(require_user_id),
):
    return c.PatientVisitController(db, actor_id=actor).update(
        visit_id, body.model_dump(exclude_unset=True)
    )


@router.delete("/patient-visits/{visit_id}", tags=VIS)
def delete_visit(
    visit_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.PatientVisitController(db, actor_id=actor).delete(visit_id)
