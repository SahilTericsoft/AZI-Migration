# Patient service (PHI)

Migrated from **GkPatientService/PatientController**. Mounted at `/patient`.

## Files
`models.py` (Patient, PatientInsurance, Allergy) · `schemas.py` · `controller.py`
(**real ported logic**) · `router.py`

## Ported business logic
- **Add** — builds the deterministic `code` (`firstName+lastName+dob`, stripped
  & lowercased, via `patient_unique_code`); if it already exists, returns the
  existing patient with `"Patient Already Exists"` (no duplicate). Otherwise
  lowercases name/ssn/degree/maritalStatus/aliasName, sets
  `isActive/isDeleted/isPasswordSet` defaults, and assigns `internalPatientId`.
- **Edit** — re-normalizes names; **union-merges** `allergieIds`; recomputes the
  dedup `code` and rejects clashes (`"Patient already exists"`).
- **Toggle / soft-delete / recover** — `isActive` flip; delete sets
  `isDeleted=true` (retained); recover clears it.
- **List** — excludes deleted by default (or *only* deleted when
  `statuses:["deleted"]`); filters by gender/createdBy/specialType/date; search
  across `code/firstName/lastName/middleName/mobileNumber` (ILIKE); paginated.
- **Validate** — duplicate-code check from name + dob.
- **Insurances** — `list_by_patient`; full CRUD.

## HIPAA
- `patients` + `patient-insurances` require a bearer token (`401` otherwise);
  every access audited. `ssn`/`password`/`drivingLicenseNumber` never returned.

## Endpoints
`POST /patients` · `/patients/list` · `/patients/validate` · `GET /patients/{id}`
· `PUT /patients/{id}` · `/patients/{id}/toggle` · `/patients/{id}/recover` ·
`DELETE /patients/{id}` · patient-insurances (+ `/by-patient/{id}`) · allergies.

## Tests
`tests/test_patient.py` — dedup code, normalization, internal id, allergy merge,
soft-delete/recover, list search/exclusions, validate, auth, SSN mask, audit (12).
