-- =====================================================================
-- AZI Backend — performance indexes (run on an existing database)
-- =====================================================================
-- Adds the indexes that speed the hot lookups. Safe + idempotent
-- (IF NOT EXISTS). On a large/production table, prefer CONCURRENTLY
-- (cannot run inside a transaction) — see note at the bottom.
-- =====================================================================

-- Patient duplicate-detection runs on every create/validate.
CREATE INDEX IF NOT EXISTS ix_patients_code ON "Patients" (code);

-- Facility / Location city & state list filters (JSON expression indexes).
CREATE INDEX IF NOT EXISTS ix_facilities_addr_city  ON "Facilities" (("addressDetails" ->> 'city'));
CREATE INDEX IF NOT EXISTS ix_facilities_addr_state ON "Facilities" (("addressDetails" ->> 'state'));
CREATE INDEX IF NOT EXISTS ix_locations_addr_city   ON "Locations"  (("addressDetails" ->> 'city'));
CREATE INDEX IF NOT EXISTS ix_locations_addr_state  ON "Locations"  (("addressDetails" ->> 'state'));

-- For a large production table, build without locking writes (run each
-- separately, NOT in a transaction):
--   CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_patients_code ON "Patients" (code);
