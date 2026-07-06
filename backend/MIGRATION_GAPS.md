# Migration gap report — AI-Portal V2 → AZI-Migration

Column/table comparison of the legacy **AI-PortalApi-V2** Sequelize models against
the migrated **AZI-Migration** SQLAlchemy schema (`schema.sql`, 68 tables).

- Source of truth (legacy): `AI-PortalApi-V2/Gk*Service/models/*Model.ts` (166 models)
- Source of truth (migrated): `backend/schema.sql`
- Auto columns (`id`, `createdAt`, `updatedAt`, `deletedAt`) are ignored.

**Headline:** 19 migrated tables are missing **~135 columns**; **~89 legacy tables**
have no migrated table at all (many intentional per `SCHEMA_CHANGES.md`, several are
likely real feature gaps — see Part 2B).

> ✅ **Part 1 RESOLVED (additive):** the 139 missing columns below were added to the
> SQLAlchemy models and applied to the DB via `migrate_add_missing_columns.sql`
> (`ADD COLUMN IF NOT EXISTS` — no existing tables/columns/data/types were changed).
> `schema.sql` was regenerated. Two adjustments: `Instruments.vendor_phone_number`
> already existed (only `created_on`/`updated_on` added); `StateCityStaticData.value`
> was **skipped** (ambiguous mapping — verify before adding). Part 2 (missing tables)
> is NOT addressed.

---

## Part 1 — Missing columns on tables that WERE migrated

### 🔴 High impact (core PHI / ordering)

**`Orders`** (GkTestOrderService) — 20 missing
`labId`, `primaryInsuranceId`, `secondaryInsuranceId`, `tertiaryInsuranceId`,
`billingMode`, `icdCodes`, `icdCodeDetails`, `allergies`, `allergieIds`,
`medicationDetails`, `integrationDetails`, `internalOrderId`, `rejectionDetails`,
`rawOrderResultData`, `priorityOrderStatus`, `resultSentToPatient`,
`externalReferenceNumber`, `sampleDraftDetails`, `isDiscarded`, `testOrderReportTitle`

**`OrderSamples`** (GkTestOrderService) — 53 missing
`testId`, `testDetails`, `biomarkerId`, `biomarkerDetails`, `isPanel`, `orderType`,
`orderSampleGroupingId`, `receivedDate`, `receivedTime`, `receivedDateTime`,
`proposedDateOfCollection`, `proposedTimeOfCollection`, `proposedDateTimeOfCollection`,
`priorityOrderStatus`, `createdByDetails`, `accessionedDetails`, `accessionedLabDetails`,
`sampleCreatedTime`, `reasonForVisit`, `advancedMDSyncStatus`, `advancedMDSyncDetails`,
`primaryInsurance`, `secondaryInsurance`, `tertiaryInsurance`, `notes`, `cptCodes`,
`cptCodeDetails`, `medicationDetails`, `sampleResultObj`, `trackingId`, `isPocTest`,
`isReflexTest`, `sampleBarcodeId`, `isFlagged`, `worklistid`, `labOsBatchId`,
`linkedSampleId`, `primarySampleId`, `isLinkedSample`, `linkedTestResults`,
`isSupplementSample`, `updatedReportData`, `isLatestReportGenerated`, `isReportAmended`,
`isResultCorrected`, `latestPdfGeneratedDate`, `isSamePdf`, `swabSite`, `internalStatus`,
`isBasicDetailsFilled`, `consentDetails`, `enableAlert`, `intakeFromCompletionTime`
> Note: the migrated repo splits ordering across `test-order`, `sample`, and `result`
> modules, so some of these may be modeled on the `OrderSamples`/`ResultSamples` tables
> under a different table — worth confirming before back-filling.

**`Patients`** (GkPatientService) — 11 missing
`patientId1`, `patientId2`, `patientId3`, `alternateId1`, `alternateId2`,
`assignedBy1`, `assignedBy2`, `assignedBy3`, `customField1`, `customField2`, `customField3`

**`PatientInsurances`** (GkPatientService) — 9 missing
`frontImage`, `backImage`, `clearingHouse`, `clearingHouseCode`, `clearingHouseId`,
`clearingHouseInsuranceId`, `CPID`, `enbotDetails`, `isEnbotChecked`

**`PatientVisits`** (GkTestOrderService) — 4 missing
`attendingDoctorSecondAndFurtherGivenName`, `attendingDoctorDegree`,
`referringDoctorSecondAndFurtherGivenName`, `referringDoctorDegree`

### 🟠 Medium impact (test/panel config, lab ops)

**`Tests`** (GkPanelService) — 16 missing
`reportFormat`, `alertLimit`, `maxLimit`, `hasOrderingLimit`, `isLinkedTest`,
`linkedTestId`, `linkedTestText`, `internalTestId`, `integrationDetails`, `loincCode`,
`lastBarcodeCount`, `processOverView`, `videoUrl`, `kitRedirectUrl`,
`normalPdfTemplatePath`, `abnormalPdfTemplatePath`

**`LabSessions`** (GkLabOsService) — 12 missing
`workflow_ids`, `step_ids`, `test_ids`, `panel_ids`, `panel_barcodes`,
`selected_test_ids`, `processed_racks`, `samples_processed`, `sessions_processed`,
`is_extraction`, `is_hybrid`, `updated_by`

**`Instruments`** (GkLabOsService) — 3 missing: `vendor_phone_number`, `created_on`, `updated_on`
**`Sops`** (GkLabOsService) — 2 missing: `created_on`, `updated_on`
**`Validations`** (GkLabOsService) — 2 missing: `created_on`, `updated_on`

### 🟡 Low impact

| Table | Service | Missing columns |
| --- | --- | --- |
| `Products` | GkInventoryService | `lastBarcodeValue`, `lastUpdatedBy` |
| `QrCodes` | GkInventoryService | `expiryTime`, `isIntakeFormAvailable` |
| `InventoryQuantities` | GkLabInventoryService | `isUpdated` |
| `Biomarkers` | GkPanelService | `internalBiomarkerId` |
| `SendoutBatches` | GkSendoutService | `labName`, `testIds` |

### ℹ️ Renamed (NOT missing — documented in SCHEMA_CHANGES.md)

| Table | Legacy → Migrated |
| --- | --- |
| `EmailLogs` | `from`→`fromAddress`, `to`→`toAddress` |
| `Notifications` | `from`→`fromUserId`, `to`→`toUserId` |
| `SmsLogs` | `to`→`toNumber` |
| `InventoryQuantities` | `order`→`orderInfo` |

> `StateCityStaticData` flagged missing `value` vs `RaceandEthnicity` — ambiguous
> static-data table mapping, verify manually (low confidence).

---

## Part 2 — Legacy tables with NO migrated table

> ✅ **Part 2 RESOLVED (additive):** all **79** missing tables (596 columns) were
> generated as SQLAlchemy models in [`services/legacy_parity/models.py`](services/legacy_parity/models.py)
> (id PK + `createdAt`/`updatedAt`, columns/types derived from the legacy Sequelize
> `.init()` definitions) and created in the DB via `create_all` (`CREATE TABLE IF NOT
> EXISTS` — nothing existing was touched). `schema.sql` now has **152 tables**. The
> module is imported in `main.py` so the models register on `Base.metadata`. These
> tables have **no routers/endpoints** — they exist for schema parity and data
> migration; wire up APIs per feature as needed. Excluded: `Allergie`/`ClearingHouse`
> (already migrated as `Allergies`/`ClearingHouses`) and `PanelOld` (dead table).

### 2A. Intentionally deferred (compute / peripheral services)
Per `SCHEMA_CHANGES.md` §3 — the new app never reads/writes these.

- **OCR**: `OCREOBBatch`, `OCREOBBatchSessionImages`, `OCREOBBatchSessionResult`,
  `OCREOBBatchSessions`, `OCRInferenceSession`, `OCRInferenceSessionImage`, `OCRUser`
- **PDF generation**: `ReportArchive`, `ReviewResult`, `UploadResultSession`,
  `ResultControlComment`, `ResultSampleComment`, `ResultSampleDetail`,
  `ResultSampleMetaDetails`
- **LabOs internals**: `LabOsBatchList`, `LabOsCapa`, `LabOsCategory`,
  `LabOsControlMapping`, `LabOsFiles`, `LabOsFolders`, `LabOsWorklist`, `Plates`,
  `VersioningFiles`, `SampleProcessingPlate`, `SampleProcessingSession`,
  `LabOsInventory`, `LabOsResultLogs`
- **Bulk upload batches**: `BatchOrderSession`, `BatchOrderSessionPatient`,
  `BatchOrderSessionValue`, `OrderStaticData`

### 2B. Core-domain tables — likely REAL feature gaps ⚠️
These back active admin/portal features and have no equivalent in the migrated schema.

- **Dynamic forms** (only `Chats` was migrated): `Question`, `QuestionForm`, `QuestionFormStep`
- **Test/Panel config**: `TestPanel`, `PanelIcdCode`, `TestQuestion`, `TestReportLayout`,
  `TestAttachments`, `PanelImage`, `PanelVariableTemplate`, `BiomarkerAttachments`,
  `BiomarkerReportConfiguration`, `BiomarkerStaticSampleTypes`
- **Lab/Location/Facility linking** (favorites, assigned tests): `LinkLabTest`,
  `LinkLabPanel`, `LinkLabBiomarker`, `LinkLocationTest`, `LinkLocationPanel`,
  `LinkLocationBiomarker`, `LinkPatientLocation`, `LocationFavoriteIcdCode`
- **Order extras**: `OrderFlag`, `OrderFlagV2`, `OrderAttachment`, `OrderExternalIds`,
  `OrderReportHeader`, `OrderSampleGrouping`, `Medication`, `SendOutOrderResult`,
  `SendOutOrderResultsArchive`
- **Result sessions**: `ResultSession`, `ResultSessionValue`
- **Patient extras**: `PatientAttachments`, `PatientExternalIds`, `PatientIntakeResponse`,
  `PatientToken`, `EnbLog`, `EnbCheckLog`
- **Inventory**: `ProductCart`, `ProductQuantity`, `ProductQuantityLog`
- **D2C**: `CustomerToken`, `CustomerKitOrderItems`
- **Lab documents/images**: `LabDocument`, `LabImage`
- **Static/reference data**: `PatientStaticData`, `FacilityStaticData`, `LabStaticData`,
  `PanelStaticData`, `BiomarkerStaticData`

> Excluded false positives: `Allergie`→`Allergies` and `ClearingHouse`→`ClearingHouses`
> ARE migrated (name-stem mismatch only). `PanelOld` is a dead legacy table.

---

*Generated by comparing Sequelize `.init()` column definitions against `schema.sql`.
Re-run: `python /path/to/schema_diff.py`.*
