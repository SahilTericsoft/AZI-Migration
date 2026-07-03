"""Patient router (PHI) — patients + insurances protected; allergies open.

Surfaces the real legacy endpoints: add (dedup), list (rich search), view, edit
(allergy merge), toggle, soft-delete, recover, validate.
"""

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from core.api import ListIn
from core.database import get_db
from core.deps import require_user_id
from services.patient import controller as c
from services.patient import schemas as s

router = APIRouter(prefix="/patient")
PAT = ["patient: patients"]
INS = ["patient: insurances"]
ALG = ["patient: allergies"]


# ------------------------------------------------------- patients (PHI)
@router.post("/patients", tags=PAT)
def add_patient(
    body: s.PatientCreate, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.PatientController(db, actor_id=actor).add(body.model_dump(exclude_unset=True))


@router.post("/patients/list", tags=PAT)
def list_patients(
    body: s.PatientListQuery, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.PatientController(db, actor_id=actor).list(body)


@router.post("/patients/validate", tags=PAT)
def validate_patient(
    body: s.ValidatePatientIn, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.PatientController(db, actor_id=actor).validate(
        body.firstName, body.lastName, body.dateOfBirth
    )


@router.get("/patients/flagged-count", tags=PAT)
def flagged_patient_count(
    db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    """Counts of patients who crossed the alert / max sample limit (for the flag button)."""
    return c.PatientController(db, actor_id=actor).flagged_count()


@router.post("/patients/bulk-upload", tags=PAT)
async def bulk_upload_patients(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    actor: int = Depends(require_user_id),
):
    """Create patients in bulk from a CSV (firstName, lastName, dateOfBirth required)."""
    content = await file.read()
    return c.PatientController(db, actor_id=actor).bulk_upload(content, actor)


@router.get("/patients/{patient_id}", tags=PAT)
def view_patient(
    patient_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.PatientController(db, actor_id=actor).view(patient_id)


@router.put("/patients/{patient_id}", tags=PAT)
def edit_patient(
    patient_id: int,
    body: s.PatientEdit,
    db: Session = Depends(get_db),
    actor: int = Depends(require_user_id),
):
    return c.PatientController(db, actor_id=actor).edit(
        patient_id, body.model_dump(exclude_unset=True)
    )


@router.put("/patients/{patient_id}/toggle", tags=PAT)
def toggle_patient(
    patient_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.PatientController(db, actor_id=actor).toggle(patient_id)


@router.put("/patients/{patient_id}/recover", tags=PAT)
def recover_patient(
    patient_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.PatientController(db, actor_id=actor).recover(patient_id)


@router.delete("/patients/{patient_id}", tags=PAT)
def delete_patient(
    patient_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.PatientController(db, actor_id=actor).soft_delete(patient_id)


# -------------------------------------------------- patient insurances (PHI)
@router.post("/patient-insurances", tags=INS)
def add_insurance(
    body: s.PatientInsuranceCreate,
    db: Session = Depends(get_db),
    actor: int = Depends(require_user_id),
):
    return c.PatientInsuranceController(db, actor_id=actor).create(
        body.model_dump(exclude_unset=True)
    )


@router.get("/patient-insurances/by-patient/{patient_id}", tags=INS)
def insurances_by_patient(
    patient_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.PatientInsuranceController(db, actor_id=actor).list_by_patient(patient_id)


@router.get("/patient-insurances/{ins_id}", tags=INS)
def get_insurance(
    ins_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.PatientInsuranceController(db, actor_id=actor).get(ins_id)


@router.put("/patient-insurances/{ins_id}", tags=INS)
def edit_insurance(
    ins_id: int,
    body: s.PatientInsuranceEdit,
    db: Session = Depends(get_db),
    actor: int = Depends(require_user_id),
):
    return c.PatientInsuranceController(db, actor_id=actor).update(
        ins_id, body.model_dump(exclude_unset=True)
    )


@router.delete("/patient-insurances/{ins_id}", tags=INS)
def delete_insurance(
    ins_id: int, db: Session = Depends(get_db), actor: int = Depends(require_user_id)
):
    return c.PatientInsuranceController(db, actor_id=actor).delete(ins_id)


# ------------------------------------------------------ allergies (reference)
@router.post("/allergies", tags=ALG)
def add_allergy(body: s.AllergyCreate, db: Session = Depends(get_db)):
    return c.AllergyController(db).create(body.model_dump(exclude_unset=True))


@router.post("/allergies/list", tags=ALG)
def list_allergies(body: ListIn, db: Session = Depends(get_db)):
    return c.AllergyController(db).list(body)


@router.get("/allergies/{allergy_id}", tags=ALG)
def get_allergy(allergy_id: int, db: Session = Depends(get_db)):
    return c.AllergyController(db).get(allergy_id)


@router.put("/allergies/{allergy_id}", tags=ALG)
def edit_allergy(allergy_id: int, body: s.AllergyEdit, db: Session = Depends(get_db)):
    return c.AllergyController(db).update(allergy_id, body.model_dump(exclude_unset=True))


@router.delete("/allergies/{allergy_id}", tags=ALG)
def delete_allergy(allergy_id: int, db: Session = Depends(get_db)):
    return c.AllergyController(db).delete(allergy_id)
