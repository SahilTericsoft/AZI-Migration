-- ============================================================================
-- PENDING DATABASE MIGRATIONS  (run once, before the next deploy)
-- ----------------------------------------------------------------------------
-- `scripts/init_db.py` only CREATEs missing tables — it never ALTERs an
-- existing one. Every new column added to an already-deployed table is
-- collected here. All statements are idempotent (IF NOT EXISTS), so this file
-- is safe to re-run.
--
-- Apply with:
--   fly ssh console -C "psql \$DATABASE_URL -f migrations/pending_migrations.sql"
-- or locally:
--   psql "$DATABASE_URL" -f migrations/pending_migrations.sql
--
-- Keep this list updated as new columns are added during the migration work.
-- ============================================================================

-- Lab onboarding: primary contact + uploaded onboarding documents
ALTER TABLE "Labs" ADD COLUMN IF NOT EXISTS "primaryContact" JSON;
ALTER TABLE "Labs" ADD COLUMN IF NOT EXISTS "attachments" JSON;

-- Test order: uploaded order documents
ALTER TABLE "Orders" ADD COLUMN IF NOT EXISTS "attachments" JSON;

-- Panel ordering limits (per-patient monthly alert / max limit -> patient flag)
ALTER TABLE "Panels" ADD COLUMN IF NOT EXISTS "hasOrderingLimit" BOOLEAN DEFAULT FALSE;
ALTER TABLE "Panels" ADD COLUMN IF NOT EXISTS "alertLimit" INTEGER;
ALTER TABLE "Panels" ADD COLUMN IF NOT EXISTS "maxLimit" INTEGER;

-- Result module: per-target reading columns on ResultSamples (run-file + manual)
ALTER TABLE "ResultSamples" ADD COLUMN IF NOT EXISTS "targetName" VARCHAR;
ALTER TABLE "ResultSamples" ADD COLUMN IF NOT EXISTS "biomarkerName" VARCHAR;
ALTER TABLE "ResultSamples" ADD COLUMN IF NOT EXISTS "fluorophore" VARCHAR;
ALTER TABLE "ResultSamples" ADD COLUMN IF NOT EXISTS "wellPosition" VARCHAR;
ALTER TABLE "ResultSamples" ADD COLUMN IF NOT EXISTS "cqValue" DOUBLE PRECISION;
ALTER TABLE "ResultSamples" ADD COLUMN IF NOT EXISTS "result" VARCHAR;
ALTER TABLE "ResultSamples" ADD COLUMN IF NOT EXISTS "value" VARCHAR;

-- Result module: new table "UploadResultSessions" is created automatically by
-- re-running scripts/init_db.py (create_all adds missing tables) — no ALTER needed.

-- Instrument module: vendor phone + attachments + preventative maintenance log
ALTER TABLE "Instruments" ADD COLUMN IF NOT EXISTS "vendor_phone_number" VARCHAR;
ALTER TABLE "Instruments" ADD COLUMN IF NOT EXISTS "attachments" JSON;
ALTER TABLE "Instruments" ADD COLUMN IF NOT EXISTS "maintenanceLogs" JSON;

-- Patient: legacy multi-identifier / custom fields (in the model since the
-- initial migration but never ALTERed onto the deployed table — any Patient
-- SELECT 500s with "column Patients.patientId1 does not exist" until applied).
ALTER TABLE "Patients" ADD COLUMN IF NOT EXISTS "patientId1" VARCHAR;
ALTER TABLE "Patients" ADD COLUMN IF NOT EXISTS "patientId2" VARCHAR;
ALTER TABLE "Patients" ADD COLUMN IF NOT EXISTS "patientId3" VARCHAR;
ALTER TABLE "Patients" ADD COLUMN IF NOT EXISTS "alternateId1" VARCHAR;
ALTER TABLE "Patients" ADD COLUMN IF NOT EXISTS "alternateId2" VARCHAR;
ALTER TABLE "Patients" ADD COLUMN IF NOT EXISTS "assignedBy1" VARCHAR;
ALTER TABLE "Patients" ADD COLUMN IF NOT EXISTS "assignedBy2" VARCHAR;
ALTER TABLE "Patients" ADD COLUMN IF NOT EXISTS "assignedBy3" VARCHAR;
ALTER TABLE "Patients" ADD COLUMN IF NOT EXISTS "customField1" VARCHAR;
ALTER TABLE "Patients" ADD COLUMN IF NOT EXISTS "customField2" VARCHAR;
ALTER TABLE "Patients" ADD COLUMN IF NOT EXISTS "customField3" VARCHAR;

-- Lab <-> catalog assignment: three new join tables ("LinkLabTests",
-- "LinkLabPanels", "LinkLabBiomarkers") are created automatically by re-running
-- scripts/init_db.py (create_all adds missing tables) — no ALTER needed.
