# Test Configuration service

Migrated from **GkPanelService** (PanelController, TestController,
BiomarkerController) + the CPT/ICD code lookups. Mounted at `/test-config`.

## Files
| File | Role |
| --- | --- |
| `models.py` | Panel, Test, Biomarker, CptCode, IcdCode |
| `schemas.py` | request bodies + rich list/lite query bodies |
| `controller.py` | **real business logic** ported from the old controllers |
| `router.py` | explicit routes → controllers |

## Ported business logic (not generic CRUD)
- **Uniqueness** — panel rejects duplicate `name+code`; test rejects duplicate
  `code` and duplicate `name+sampleType`; biomarker/CPT/ICD reject duplicate
  code. Edits run the same check excluding the current row.
- **Normalization** — `code → UPPER`, `sampleType`/`sampleCollectionDeviceName →
  lower`, names trimmed.
- **Internal id** — panels get `internalPanelId` = `{INSTANCE}_{YYYYMMDD}_{NNNN}`
  (a per-day sequence), via `core/ids.daily_sequence_id`.
- **Status + draft-aware toggle** — new panels default `status="completed"`,
  tests/biomarkers `"draft"`; `toggle` refuses to activate a `draft` and flips
  `isActive` otherwise.
- **Rich list** — filters by `createdByIds`, `search` (name/code, ILIKE),
  `statuses` (active/inactive/draft/completed), `startDate`/`endDate`, `sort`;
  paginates; adds `statusObj`; populates `createdByDetails` from Users via
  `core/populate.attach_created_by` (single query, no N+1).

## Endpoints
| Method | Path | Action |
| --- | --- | --- |
| POST | `/test-config/{panels\|tests\|biomarkers}` | add (uniqueness/normalize/internal-id) |
| POST | `/…/{entity}/list` | rich filtered + paginated list (+ createdByDetails) |
| POST | `/…/{entity}/list-lite` | id/search/active filtered lite list |
| POST | `/…/{entity}/check-code` | code-duplicate check |
| GET | `/…/{entity}/{id}` | view |
| PUT | `/…/{entity}/{id}` | edit (uniqueness excl self) |
| PUT | `/…/{entity}/{id}/toggle` | draft-aware activate/deactivate |
| DELETE | `/…/{entity}/{id}` | delete |
| — | `/test-config/{cpt-codes\|icd-codes}` | add/list/view/edit/delete (code-unique) |

## Tests
`tests/test_test_config.py` — uniqueness, normalization, internal-id, toggle
(draft block), list filters + population, list-lite, check-code (13 tests).
