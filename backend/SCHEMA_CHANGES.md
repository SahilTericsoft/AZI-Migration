# Database — changes vs legacy & how to sync

Two SQL artifacts are provided in `backend/`:

| File | Use it when |
| --- | --- |
| **`schema.sql`** | You want a **fresh/empty** database with the full new schema (all **68** tables, `CREATE TABLE IF NOT EXISTS`). |
| **`migrate_legacy.sql`** | You want to point the new app at your **existing legacy** database (applies only the deltas). |

Both were generated from the SQLAlchemy models and **validated against a real
PostgreSQL instance** (applies cleanly, 68 tables, 0 errors).

---

## What changed vs the legacy schema

The migration deliberately **preserved table names and column names 1:1** (incl.
camelCase) so the new service can run on the existing database. Only the
following changes exist:

### 1. Column renames (4 tables, 6 columns)
The legacy DB used SQL-reserved / language-keyword column names. These were
renamed so they're safe in Python/SQLAlchemy:

| Table | Legacy column | New column |
| --- | --- | --- |
| `Notifications` | `from` | `fromUserId` |
| `Notifications` | `to` | `toUserId` |
| `EmailLogs` | `from` | `fromAddress` |
| `EmailLogs` | `to` | `toAddress` |
| `SmsLogs` | `to` | `toNumber` |
| `InventoryQuantities` | `order` | `orderInfo` |

### 2. New table: `AuditLogs`
A HIPAA audit trail that did **not** exist in legacy — records who/what/when on
every PHI access (`userId, action, entity, recordId, details, createdAt`).

### 3. Scope: 68 of 151 tables
The new backend models the **68 core-domain tables**. The other ~83 legacy
tables belong to the **deferred compute services** (PDF/HL7/ML/OCR-runtime/SFTP,
plus peripheral LabOs sub-tables) and are **left untouched** — the new app never
reads or writes them.

### 4. No changes you need to worry about
- **No type changes** on existing columns (ARRAY/JSON/JSONB and the camelCase
  names are identical; e.g. `StateCityStaticData.isActive` stays `VARCHAR`).
- **No foreign-key constraints added** — FKs remain plain integer columns, as in
  the legacy Sequelize schema (referential integrity is enforced in the app).
- `Tokens` continues to use `expiryTime` (its real legacy column).

---

## How to sync

### Option A — fresh / staging database
```bash
createdb azi_db
psql -d azi_db -f backend/schema.sql      # creates all 68 tables
# then point the app at it:
#   DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/azi_db
```
Or, from the app itself (same result, via the models):
```bash
cd backend && source .venv/bin/activate
python -m scripts.init_db
```

### Option B — onto your existing legacy database  ⚠️ back up first
```bash
pg_dump <your_db> > backup_before_sync.sql      # ALWAYS back up
psql -d <your_db> -f backend/migrate_legacy.sql # 6 renames + AuditLogs
```
After that, set `DATABASE_URL` to the legacy DB and the app runs against it.

> **Caveat for Option B:** the new models cover a *focused subset* of columns on
> the big tables (e.g. `Patients`, `OrderSamples`). That's fine — the app only
> selects/writes the columns it models, and the legacy extras are nullable. If
> any legacy column is `NOT NULL` **without** a default, give it a default before
> go-live so app-side inserts succeed.

---

## Re-generating these files
```bash
cd backend && source .venv/bin/activate
python -m scripts.dump_schema > schema.sql    # regenerates the full DDL
```

---

## Recommendation
For long-term schema management, adopt **Alembic** (autogenerate migrations from
the models) before running against production data, so future model changes ship
as versioned, reversible migrations instead of hand-edited SQL. (Also noted in
`AUDIT.md` §9.)
