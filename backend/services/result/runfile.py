"""qPCR run-file parser (Bio-Rad CFX Maestro CSV export).

The file has a metadata header block (key,value rows) followed by a data table:
    Well, Fluor, Target, Content, Sample, Cq, Starting Quantity (SQ)

`Content` is one of: Unkn (patient sample), NTC (no-template control),
Pos Ctrl (positive control). `Sample` carries the accession id for unknowns.
`Cq` is the threshold cycle (float) or NaN when there is no amplification.

We split rows into per-accession sample readings and control readings, and call
each target Detected / Not Detected against a Cq cutoff.
"""

from __future__ import annotations

import csv
import io
import math

# A target amplifying at/under this Cq is called "Detected".
DEFAULT_CQ_CUTOFF = 40.0
UNKNOWN_CONTENTS = {"unkn", "unknown"}


def _to_cq(raw: str) -> float | None:
    try:
        v = float(raw)
        return None if math.isnan(v) else v
    except (TypeError, ValueError):
        return None


def call_result(cq: float | None, cutoff: float = DEFAULT_CQ_CUTOFF) -> str:
    return "Detected" if cq is not None and cq <= cutoff else "Not Detected"


def parse_runfile(content: bytes, cutoff: float = DEFAULT_CQ_CUTOFF) -> dict:
    """Parse a CFX qPCR CSV into {metadata, controls[], samples{accession: [...]}}."""
    text = content.decode("utf-8-sig", errors="replace")
    rows = list(csv.reader(io.StringIO(text)))

    metadata: dict[str, str] = {}
    header_idx: int | None = None
    for i, row in enumerate(rows):
        if not row:
            continue
        first = (row[0] or "").strip()
        if first == "Well" and len(row) > 1 and (row[1] or "").strip() == "Fluor":
            header_idx = i
            break
        if first and len(row) > 1 and (row[1] or "").strip():
            metadata[first] = (row[1] or "").strip()

    controls: list[dict] = []
    samples: dict[str, list[dict]] = {}
    if header_idx is None:
        return {"metadata": metadata, "controls": controls, "samples": samples}

    header = [(h or "").strip() for h in rows[header_idx]]
    idx = {name: i for i, name in enumerate(header)}

    def get(row: list[str], name: str) -> str:
        i = idx.get(name)
        return (row[i] or "").strip() if i is not None and i < len(row) else ""

    for row in rows[header_idx + 1:]:
        if not row or not (row[0] or "").strip():
            continue
        content = get(row, "Content")
        target = get(row, "Target")
        cq = _to_cq(get(row, "Cq"))
        rec = {
            "wellPosition": get(row, "Well"),
            "fluorophore": get(row, "Fluor"),
            "targetName": target,
            "biomarkerName": target,
            "ctValue": cq,
            "result": call_result(cq, cutoff),
            "content": content,
            "sample": get(row, "Sample"),
        }
        if content.lower() in UNKNOWN_CONTENTS:
            samples.setdefault(rec["sample"], []).append(rec)
        else:
            rec["control"] = content
            controls.append(rec)

    return {"metadata": metadata, "controls": controls, "samples": samples}
