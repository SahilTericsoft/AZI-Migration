"""Seed the BiomarkerStaticSampleTypes table with the default sample types +
collection devices, so the Test/Panel wizard dropdowns are DB-backed (editable)
instead of falling back to the built-in constant.

Idempotent — only inserts a sample type if its name is not already present. Run
from backend root:

    .venv/bin/python -m scripts.seed_sample_types
"""

from __future__ import annotations

from datetime import datetime, timezone

from core.database import SessionLocal
from services.legacy_parity.models import BiomarkerStaticSampleTypes as SampleTypeRow
from services.static_data.router import SAMPLE_TYPES_WITH_DEVICES


def main() -> None:
    db = SessionLocal()
    inserted = 0
    try:
        existing = {
            (r.sampleType or "").lower() for r in db.query(SampleTypeRow.sampleType).all()
        }
        now = datetime.now(timezone.utc)
        for entry in SAMPLE_TYPES_WITH_DEVICES:
            if entry["sampleType"].lower() in existing:
                continue
            db.add(
                SampleTypeRow(
                    sampleType=entry["sampleType"],
                    sampleCollectionDeviceName=entry["sampleCollectionDeviceName"],
                    createdAt=now,
                    updatedAt=now,
                )
            )
            inserted += 1
        db.commit()
        total = db.query(SampleTypeRow).count()
        print(f"Seeded {inserted} sample types (table now has {total}).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
