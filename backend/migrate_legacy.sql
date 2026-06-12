-- =====================================================================
-- AZI Backend — sync an EXISTING legacy database to the new app
-- =====================================================================
-- Run this ONLY against your existing (legacy) PostgreSQL database.
-- It applies the few deltas the new backend needs; all other legacy
-- tables/columns already match (table + column names were preserved 1:1).
--
-- Idempotent-ish: the renames will error if already applied — that's safe
-- to ignore, or guard each with a DO block. The AuditLogs create is guarded.
--
-- Always take a backup first:  pg_dump <db> > backup_before_sync.sql
-- =====================================================================

BEGIN;

-- 1) Column renames (legacy used SQL-reserved / Python-keyword names) -------
ALTER TABLE "Notifications"        RENAME COLUMN "from"  TO "fromUserId";
ALTER TABLE "Notifications"        RENAME COLUMN "to"    TO "toUserId";
ALTER TABLE "EmailLogs"            RENAME COLUMN "from"  TO "fromAddress";
ALTER TABLE "EmailLogs"            RENAME COLUMN "to"    TO "toAddress";
ALTER TABLE "SmsLogs"              RENAME COLUMN "to"    TO "toNumber";
ALTER TABLE "InventoryQuantities"  RENAME COLUMN "order" TO "orderInfo";

-- 2) New table: HIPAA audit trail (did not exist in legacy) ----------------
CREATE TABLE IF NOT EXISTS "AuditLogs" (
    id        SERIAL NOT NULL,
    "userId"  INTEGER,
    action    VARCHAR NOT NULL,
    entity    VARCHAR NOT NULL,
    "recordId" INTEGER,
    details   JSON,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    PRIMARY KEY (id)
);
CREATE INDEX IF NOT EXISTS ix_auditlogs_entity   ON "AuditLogs" (entity);
CREATE INDEX IF NOT EXISTS ix_auditlogs_recordid ON "AuditLogs" ("recordId");
CREATE INDEX IF NOT EXISTS ix_auditlogs_userid   ON "AuditLogs" ("userId");

COMMIT;

-- That's it. The new backend can now point DATABASE_URL at this database.
-- (The new app only reads/writes the 68 tables it models; any other legacy
--  tables are left untouched.)
