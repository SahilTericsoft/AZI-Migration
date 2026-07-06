-- ============================================================================
-- AZI Migration — add columns missing vs legacy AI-Portal V2 (see MIGRATION_GAPS.md)
-- Idempotent & additive: ADD COLUMN IF NOT EXISTS only. Does NOT touch existing
-- tables, columns, data, or types. Safe to run multiple times.
-- ============================================================================

-- Orders (+20)
ALTER TABLE "Orders" ADD COLUMN IF NOT EXISTS "labId" INTEGER;
ALTER TABLE "Orders" ADD COLUMN IF NOT EXISTS "primaryInsuranceId" INTEGER;
ALTER TABLE "Orders" ADD COLUMN IF NOT EXISTS "secondaryInsuranceId" INTEGER;
ALTER TABLE "Orders" ADD COLUMN IF NOT EXISTS "tertiaryInsuranceId" INTEGER;
ALTER TABLE "Orders" ADD COLUMN IF NOT EXISTS "billingMode" VARCHAR;
ALTER TABLE "Orders" ADD COLUMN IF NOT EXISTS "icdCodes" VARCHAR[];
ALTER TABLE "Orders" ADD COLUMN IF NOT EXISTS "icdCodeDetails" JSON[];
ALTER TABLE "Orders" ADD COLUMN IF NOT EXISTS "allergies" VARCHAR[];
ALTER TABLE "Orders" ADD COLUMN IF NOT EXISTS "allergieIds" INTEGER[];
ALTER TABLE "Orders" ADD COLUMN IF NOT EXISTS "medicationDetails" JSON[];
ALTER TABLE "Orders" ADD COLUMN IF NOT EXISTS "integrationDetails" JSON;
ALTER TABLE "Orders" ADD COLUMN IF NOT EXISTS "internalOrderId" VARCHAR;
ALTER TABLE "Orders" ADD COLUMN IF NOT EXISTS "rejectionDetails" JSON;
ALTER TABLE "Orders" ADD COLUMN IF NOT EXISTS "rawOrderResultData" JSON;
ALTER TABLE "Orders" ADD COLUMN IF NOT EXISTS "priorityOrderStatus" VARCHAR;
ALTER TABLE "Orders" ADD COLUMN IF NOT EXISTS "resultSentToPatient" BOOLEAN;
ALTER TABLE "Orders" ADD COLUMN IF NOT EXISTS "externalReferenceNumber" VARCHAR;
ALTER TABLE "Orders" ADD COLUMN IF NOT EXISTS "sampleDraftDetails" JSON;
ALTER TABLE "Orders" ADD COLUMN IF NOT EXISTS "isDiscarded" BOOLEAN;
ALTER TABLE "Orders" ADD COLUMN IF NOT EXISTS "testOrderReportTitle" VARCHAR;

-- PatientVisits (+4)
ALTER TABLE "PatientVisits" ADD COLUMN IF NOT EXISTS "attendingDoctorSecondAndFurtherGivenName" VARCHAR;
ALTER TABLE "PatientVisits" ADD COLUMN IF NOT EXISTS "attendingDoctorDegree" VARCHAR;
ALTER TABLE "PatientVisits" ADD COLUMN IF NOT EXISTS "referringDoctorSecondAndFurtherGivenName" VARCHAR;
ALTER TABLE "PatientVisits" ADD COLUMN IF NOT EXISTS "referringDoctorDegree" VARCHAR;

-- OrderSamples (+53)
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "testId" INTEGER;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "testDetails" JSON;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "biomarkerId" INTEGER;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "biomarkerDetails" JSON;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "isPanel" BOOLEAN;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "orderType" VARCHAR;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "orderSampleGroupingId" INTEGER;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "receivedDate" VARCHAR;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "receivedTime" VARCHAR;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "receivedDateTime" VARCHAR;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "proposedDateOfCollection" VARCHAR;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "proposedTimeOfCollection" VARCHAR;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "proposedDateTimeOfCollection" VARCHAR;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "priorityOrderStatus" VARCHAR;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "createdByDetails" JSON;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "accessionedDetails" JSON;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "accessionedLabDetails" JSON;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "sampleCreatedTime" JSON;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "reasonForVisit" VARCHAR;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "advancedMDSyncStatus" VARCHAR;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "advancedMDSyncDetails" JSON;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "primaryInsurance" JSON;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "secondaryInsurance" JSON;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "tertiaryInsurance" JSON;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "notes" TEXT;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "cptCodes" VARCHAR[];
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "cptCodeDetails" JSON[];
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "medicationDetails" JSON[];
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "sampleResultObj" JSON;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "trackingId" VARCHAR;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "isPocTest" BOOLEAN;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "isReflexTest" BOOLEAN;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "sampleBarcodeId" VARCHAR;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "isFlagged" BOOLEAN;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "worklistid" INTEGER;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "labOsBatchId" INTEGER;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "linkedSampleId" INTEGER;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "primarySampleId" INTEGER;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "isLinkedSample" BOOLEAN;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "linkedTestResults" JSON;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "isSupplementSample" BOOLEAN;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "updatedReportData" JSON;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "isLatestReportGenerated" BOOLEAN;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "isReportAmended" BOOLEAN;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "isResultCorrected" BOOLEAN;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "latestPdfGeneratedDate" VARCHAR;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "isSamePdf" BOOLEAN;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "swabSite" VARCHAR;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "internalStatus" VARCHAR;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "isBasicDetailsFilled" BOOLEAN;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "consentDetails" JSON;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "enableAlert" BOOLEAN;
ALTER TABLE "OrderSamples" ADD COLUMN IF NOT EXISTS "intakeFromCompletionTime" JSON;

-- Patients (+11)
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

-- PatientInsurances (+9)
ALTER TABLE "PatientInsurances" ADD COLUMN IF NOT EXISTS "frontImage" JSON;
ALTER TABLE "PatientInsurances" ADD COLUMN IF NOT EXISTS "backImage" JSON;
ALTER TABLE "PatientInsurances" ADD COLUMN IF NOT EXISTS "clearingHouse" VARCHAR;
ALTER TABLE "PatientInsurances" ADD COLUMN IF NOT EXISTS "clearingHouseCode" VARCHAR;
ALTER TABLE "PatientInsurances" ADD COLUMN IF NOT EXISTS "clearingHouseId" INTEGER;
ALTER TABLE "PatientInsurances" ADD COLUMN IF NOT EXISTS "clearingHouseInsuranceId" INTEGER;
ALTER TABLE "PatientInsurances" ADD COLUMN IF NOT EXISTS "CPID" VARCHAR;
ALTER TABLE "PatientInsurances" ADD COLUMN IF NOT EXISTS "enbotDetails" JSON;
ALTER TABLE "PatientInsurances" ADD COLUMN IF NOT EXISTS "isEnbotChecked" BOOLEAN;

-- Biomarkers (+1)
ALTER TABLE "Biomarkers" ADD COLUMN IF NOT EXISTS "internalBiomarkerId" VARCHAR;

-- Tests (+16)
ALTER TABLE "Tests" ADD COLUMN IF NOT EXISTS "reportFormat" VARCHAR;
ALTER TABLE "Tests" ADD COLUMN IF NOT EXISTS "alertLimit" NUMERIC;
ALTER TABLE "Tests" ADD COLUMN IF NOT EXISTS "maxLimit" NUMERIC;
ALTER TABLE "Tests" ADD COLUMN IF NOT EXISTS "hasOrderingLimit" BOOLEAN;
ALTER TABLE "Tests" ADD COLUMN IF NOT EXISTS "isLinkedTest" BOOLEAN;
ALTER TABLE "Tests" ADD COLUMN IF NOT EXISTS "linkedTestId" NUMERIC;
ALTER TABLE "Tests" ADD COLUMN IF NOT EXISTS "linkedTestText" VARCHAR;
ALTER TABLE "Tests" ADD COLUMN IF NOT EXISTS "internalTestId" VARCHAR;
ALTER TABLE "Tests" ADD COLUMN IF NOT EXISTS "integrationDetails" JSON;
ALTER TABLE "Tests" ADD COLUMN IF NOT EXISTS "loincCode" VARCHAR;
ALTER TABLE "Tests" ADD COLUMN IF NOT EXISTS "lastBarcodeCount" INTEGER;
ALTER TABLE "Tests" ADD COLUMN IF NOT EXISTS "processOverView" VARCHAR;
ALTER TABLE "Tests" ADD COLUMN IF NOT EXISTS "videoUrl" VARCHAR;
ALTER TABLE "Tests" ADD COLUMN IF NOT EXISTS "kitRedirectUrl" VARCHAR;
ALTER TABLE "Tests" ADD COLUMN IF NOT EXISTS "normalPdfTemplatePath" VARCHAR;
ALTER TABLE "Tests" ADD COLUMN IF NOT EXISTS "abnormalPdfTemplatePath" VARCHAR;

-- Instruments (+2)
ALTER TABLE "Instruments" ADD COLUMN IF NOT EXISTS "created_on" TIMESTAMP WITH TIME ZONE;
ALTER TABLE "Instruments" ADD COLUMN IF NOT EXISTS "updated_on" TIMESTAMP WITH TIME ZONE;

-- Sops (+2)
ALTER TABLE "Sops" ADD COLUMN IF NOT EXISTS "created_on" TIMESTAMP WITH TIME ZONE;
ALTER TABLE "Sops" ADD COLUMN IF NOT EXISTS "updated_on" TIMESTAMP WITH TIME ZONE;

-- Validations (+2)
ALTER TABLE "Validations" ADD COLUMN IF NOT EXISTS "created_on" TIMESTAMP WITH TIME ZONE;
ALTER TABLE "Validations" ADD COLUMN IF NOT EXISTS "updated_on" TIMESTAMP WITH TIME ZONE;

-- LabSessions (+12)
ALTER TABLE "LabSessions" ADD COLUMN IF NOT EXISTS "workflow_ids" JSON;
ALTER TABLE "LabSessions" ADD COLUMN IF NOT EXISTS "step_ids" JSON;
ALTER TABLE "LabSessions" ADD COLUMN IF NOT EXISTS "test_ids" JSON;
ALTER TABLE "LabSessions" ADD COLUMN IF NOT EXISTS "panel_ids" JSON;
ALTER TABLE "LabSessions" ADD COLUMN IF NOT EXISTS "panel_barcodes" JSON;
ALTER TABLE "LabSessions" ADD COLUMN IF NOT EXISTS "selected_test_ids" JSON;
ALTER TABLE "LabSessions" ADD COLUMN IF NOT EXISTS "processed_racks" JSON;
ALTER TABLE "LabSessions" ADD COLUMN IF NOT EXISTS "samples_processed" JSON;
ALTER TABLE "LabSessions" ADD COLUMN IF NOT EXISTS "sessions_processed" INTEGER[];
ALTER TABLE "LabSessions" ADD COLUMN IF NOT EXISTS "is_extraction" BOOLEAN;
ALTER TABLE "LabSessions" ADD COLUMN IF NOT EXISTS "is_hybrid" BOOLEAN;
ALTER TABLE "LabSessions" ADD COLUMN IF NOT EXISTS "updated_by" INTEGER;

-- Products (+2)
ALTER TABLE "Products" ADD COLUMN IF NOT EXISTS "lastBarcodeValue" INTEGER;
ALTER TABLE "Products" ADD COLUMN IF NOT EXISTS "lastUpdatedBy" INTEGER;

-- QrCodes (+2)
ALTER TABLE "QrCodes" ADD COLUMN IF NOT EXISTS "expiryTime" VARCHAR;
ALTER TABLE "QrCodes" ADD COLUMN IF NOT EXISTS "isIntakeFormAvailable" BOOLEAN;

-- InventoryQuantities (+1)
ALTER TABLE "InventoryQuantities" ADD COLUMN IF NOT EXISTS "isUpdated" BOOLEAN;

-- SendoutBatches (+2)
ALTER TABLE "SendoutBatches" ADD COLUMN IF NOT EXISTS "labName" VARCHAR;
ALTER TABLE "SendoutBatches" ADD COLUMN IF NOT EXISTS "testIds" JSON[];

-- Total columns added: 139