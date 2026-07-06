-- =====================================================================
-- AZI Backend — full database schema (PostgreSQL)
-- Generated from the SQLAlchemy models. 152 tables.
-- Safe to run on an empty DB or to add missing tables/indexes (IF NOT EXISTS).
--
-- NOTE: foreign keys are modeled as plain integer columns (no FK
-- constraints) to mirror the legacy Sequelize schema 1:1. See
-- SCHEMA_CHANGES.md for changes vs the legacy schema.
-- =====================================================================


CREATE TABLE IF NOT EXISTS "ACLModulesMappings" (
	id SERIAL NOT NULL, 
	module VARCHAR, 
	feature VARCHAR, 
	description VARCHAR, 
	code VARCHAR, 
	apis VARCHAR[], 
	"isPrimary" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "ActivityLogs" (
	id SERIAL NOT NULL, 
	module VARCHAR, 
	feature VARCHAR, 
	field VARCHAR, 
	value TEXT, 
	type VARCHAR, 
	action VARCHAR, 
	"userId" INTEGER, 
	"identityId" INTEGER, 
	"logDateTime" VARCHAR, 
	data JSON, 
	"reasonForEdit" VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_ActivityLogs_identityId" ON "ActivityLogs" ("identityId");

CREATE INDEX IF NOT EXISTS "ix_ActivityLogs_userId" ON "ActivityLogs" ("userId");

CREATE TABLE IF NOT EXISTS "AdvancedMDTokens" (
	id SERIAL NOT NULL, 
	"userName" VARCHAR, 
	"loginPageUrl" VARCHAR, 
	"officeKey" VARCHAR, 
	token TEXT, 
	expiry TIMESTAMP WITH TIME ZONE, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "Allergies" (
	id SERIAL NOT NULL, 
	name VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "AuditLogs" (
	id SERIAL NOT NULL, 
	"userId" INTEGER, 
	action VARCHAR NOT NULL, 
	entity VARCHAR NOT NULL, 
	"recordId" INTEGER, 
	details JSON, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_AuditLogs_entity" ON "AuditLogs" (entity);

CREATE INDEX IF NOT EXISTS "ix_AuditLogs_recordId" ON "AuditLogs" ("recordId");

CREATE INDEX IF NOT EXISTS "ix_AuditLogs_userId" ON "AuditLogs" ("userId");

CREATE TABLE IF NOT EXISTS "BarcodeSessions" (
	id SERIAL NOT NULL, 
	title VARCHAR, 
	"attachmentDetails" JSON, 
	"testName" VARCHAR, 
	"testId" INTEGER, 
	quantity INTEGER, 
	"createdByDetails" JSON, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "Barcodes" (
	id SERIAL NOT NULL, 
	barcode VARCHAR, 
	"testId" INTEGER, 
	"testName" VARCHAR, 
	purpose VARCHAR, 
	"isAvailable" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_Barcodes_barcode" ON "Barcodes" (barcode);

CREATE TABLE IF NOT EXISTS "BatchOrderSession" (
	id SERIAL NOT NULL, 
	title VARCHAR, 
	"facilityDetails" JSON, 
	"locationDetails" JSON, 
	"panelDetails" JSON, 
	"testDetails" JSON, 
	"physicianDetails" JSON, 
	"numberOfOrders" INTEGER, 
	"numberOfValidOrders" INTEGER, 
	"numberOfInValidOrders" INTEGER, 
	"isGenerated" BOOLEAN, 
	"isValid" BOOLEAN, 
	"dataColumns" VARCHAR[], 
	"createdByDetails" JSON, 
	"attachmentDetails" JSON, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "BatchOrderSessionPatient" (
	id SERIAL NOT NULL, 
	title VARCHAR, 
	"facilityDetails" JSON, 
	"locationDetails" JSON, 
	"numberOfPatients" INTEGER, 
	"numberOfValidPatients" INTEGER, 
	"numberOfInValidPatients" INTEGER, 
	"isGenerated" BOOLEAN, 
	"isValid" BOOLEAN, 
	"dataColumns" VARCHAR[], 
	"createdByDetails" JSON, 
	"attachmentDetails" JSON, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "BatchOrderSessionValue" (
	id SERIAL NOT NULL, 
	"batchOrderSessionId" INTEGER, 
	"facilityDetails" JSON, 
	"locationDetails" JSON, 
	"physicianDetails" JSON, 
	"patientDetails" JSON, 
	"panelDetails" JSON, 
	"testDetails" JSON, 
	"createdByDetails" JSON, 
	barcode VARCHAR, 
	"dateOfCollection" VARCHAR, 
	"timeOfCollection" VARCHAR, 
	"externalReferenceNumber" VARCHAR, 
	"dateTimeOfCollection" JSON, 
	"sendResultToPatient" BOOLEAN, 
	"modeOfPayment" VARCHAR, 
	status VARCHAR, 
	"isGenerated" BOOLEAN, 
	"isPriorityOrder" BOOLEAN, 
	"isValid" BOOLEAN, 
	"isConsentSigned" BOOLEAN, 
	"labDetails" JSON, 
	"reasonForVisit" VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "BiomarkerAttachments" (
	id SERIAL NOT NULL, 
	"biomarkerId" INTEGER, 
	"fileName" VARCHAR, 
	"mimeType" VARCHAR, 
	"fileSize" INTEGER, 
	path VARCHAR, 
	"secureUrl" VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "BiomarkerReportConfiguration" (
	id SERIAL NOT NULL, 
	"biomarkerId" INTEGER, 
	gender VARCHAR, 
	age VARCHAR, 
	rules JSON[], 
	"expectedResults" VARCHAR, 
	"biomarkerNotes" TEXT, 
	"isBiomarkerNoteAvailable" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "BiomarkerStaticData" (
	id SERIAL NOT NULL, 
	title VARCHAR, 
	value JSON[], 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "BiomarkerStaticSampleTypes" (
	id SERIAL NOT NULL, 
	"sampleType" VARCHAR, 
	"sampleCollectionDeviceName" JSON[], 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "Biomarkers" (
	id SERIAL NOT NULL, 
	name VARCHAR, 
	code VARCHAR, 
	"sampleType" VARCHAR, 
	"sampleCollectionDeviceName" VARCHAR, 
	description TEXT, 
	"reportFormat" VARCHAR, 
	"isActive" BOOLEAN, 
	status VARCHAR, 
	"createdBy" INTEGER, 
	"isConfigurationRequired" BOOLEAN, 
	"isPocConfigReq" BOOLEAN, 
	"pocConfigArr" VARCHAR[], 
	"biomarkerLayoutDetails" JSONB[], 
	"isIndividuallyOffered" BOOLEAN, 
	"departmentIds" INTEGER[], 
	"reagentIds" INTEGER[], 
	"instrumentIds" INTEGER[], 
	"internalBiomarkerId" VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "Chats" (
	id SERIAL NOT NULL, 
	icon VARCHAR, 
	"chatData" JSON[], 
	"stepData" JSON[], 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "ClearingHouseInsurances" (
	id SERIAL NOT NULL, 
	"clearingHouseId" INTEGER, 
	"payerName" VARCHAR, 
	"payerId" VARCHAR, 
	"CPID" VARCHAR, 
	type VARCHAR, 
	"groupId" VARCHAR, 
	"realTimePayerId" VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_ClearingHouseInsurances_clearingHouseId" ON "ClearingHouseInsurances" ("clearingHouseId");

CREATE TABLE IF NOT EXISTS "ClearingHouses" (
	id SERIAL NOT NULL, 
	"clearingHouse" VARCHAR, 
	"clearingHouseCode" VARCHAR, 
	"isActive" BOOLEAN, 
	"createdBy" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "CptCodes" (
	id SERIAL NOT NULL, 
	"cptCode" VARCHAR, 
	description TEXT, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "CustomerAddresses" (
	id SERIAL NOT NULL, 
	address1 VARCHAR, 
	address2 VARCHAR, 
	zipcode INTEGER, 
	state VARCHAR, 
	county VARCHAR, 
	city VARCHAR, 
	"mobileNumber" VARCHAR, 
	"isDefault" BOOLEAN, 
	"addedBy" INTEGER, 
	"customerId" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_CustomerAddresses_customerId" ON "CustomerAddresses" ("customerId");

CREATE TABLE IF NOT EXISTS "CustomerCarts" (
	id SERIAL NOT NULL, 
	"productId" NUMERIC, 
	quantity NUMERIC, 
	"addedBy" NUMERIC, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "CustomerToken" (
	id SERIAL NOT NULL, 
	"customerId" INTEGER, 
	token TEXT, 
	"expiryDate" VARCHAR, 
	"isActive" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "Customers" (
	id SERIAL NOT NULL, 
	"firstName" VARCHAR, 
	"lastName" VARCHAR, 
	"dateOfBirth" VARCHAR, 
	"mobileNumber" VARCHAR, 
	"emailId" VARCHAR, 
	password VARCHAR, 
	"patientId" INTEGER, 
	"isVerified" BOOLEAN, 
	"isActive" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_Customers_emailId" ON "Customers" ("emailId");

CREATE TABLE IF NOT EXISTS "D2C_CustomerOrderItems" (
	id SERIAL NOT NULL, 
	"orderId" NUMERIC, 
	"orderCode" VARCHAR, 
	"customerId" NUMERIC, 
	"patientId" NUMERIC, 
	"productId" NUMERIC, 
	quantity NUMERIC, 
	price NUMERIC, 
	"totalPrice" NUMERIC, 
	"testId" NUMERIC, 
	"dateOfOrder" TIMESTAMP WITH TIME ZONE, 
	status VARCHAR, 
	"reasonForCancellation" VARCHAR, 
	"paymentStatus" VARCHAR, 
	"paymentDate" TIMESTAMP WITH TIME ZONE, 
	"paymentMode" VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "D2C_CustomerOrders" (
	id SERIAL NOT NULL, 
	"orderCode" VARCHAR, 
	"customerId" NUMERIC, 
	"patientId" NUMERIC, 
	"dateOfOrder" TIMESTAMP WITH TIME ZONE, 
	"paymentStatus" VARCHAR, 
	"paymentDate" TIMESTAMP WITH TIME ZONE, 
	"paymentMode" VARCHAR, 
	address JSON, 
	summary JSON, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_D2C_CustomerOrders_orderCode" ON "D2C_CustomerOrders" ("orderCode");

CREATE TABLE IF NOT EXISTS "Departments" (
	id SERIAL NOT NULL, 
	name VARCHAR, 
	code VARCHAR, 
	"createdBy" INTEGER, 
	"reportType" VARCHAR[], 
	"reportFormat" VARCHAR[], 
	"isActive" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "EmailLogs" (
	id SERIAL NOT NULL, 
	"fromAddress" VARCHAR, 
	"toAddress" VARCHAR, 
	purpose VARCHAR, 
	message TEXT, 
	"isDelivered" BOOLEAN, 
	error VARCHAR, 
	"providerResponse" JSON, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_EmailLogs_toAddress" ON "EmailLogs" ("toAddress");

CREATE TABLE IF NOT EXISTS "EmailSecurities" (
	id SERIAL NOT NULL, 
	code VARCHAR, 
	"emailId" VARCHAR, 
	purpose VARCHAR, 
	"expiryTime" VARCHAR, 
	"isActive" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_EmailSecurities_emailId" ON "EmailSecurities" ("emailId");

CREATE TABLE IF NOT EXISTS "EmailTemplets" (
	id SERIAL NOT NULL, 
	purpose VARCHAR, 
	templet TEXT, 
	"isActive" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "EnbCheckLogs" (
	id SERIAL NOT NULL, 
	"controlNumber" INTEGER, 
	"patientId" INTEGER, 
	"patientInsuranceId" INTEGER, 
	"orderId" INTEGER, 
	"orderInsuranceId" INTEGER, 
	"enbServiceProviderName" VARCHAR, 
	"requestRawJsonBody" JSON, 
	"requestDataFileURL" VARCHAR, 
	"responseRawJsonBody" JSON, 
	"responseDataFileURL" VARCHAR, 
	"createdBy" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "EnbLog" (
	id SERIAL NOT NULL, 
	"patientId" INTEGER, 
	"patientInsuranceId" INTEGER, 
	"finalJson" JSON, 
	"formattedJson" JSON, 
	error JSON, 
	"createdBy" INTEGER, 
	"controlNumber" VARCHAR, 
	payload JSON, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "Facilities" (
	id SERIAL NOT NULL, 
	name VARCHAR, 
	code VARCHAR, 
	type VARCHAR, 
	"primaryContactDetails" JSON, 
	panels INTEGER[], 
	physicians INTEGER[], 
	"adminId" INTEGER, 
	"addressDetails" JSON, 
	"createdBy" INTEGER, 
	status VARCHAR, 
	"isActive" BOOLEAN, 
	"isDroidAllowed" BOOLEAN, 
	"allowAdvancedFunctionality" BOOLEAN, 
	"lastCompletedStep" INTEGER, 
	"isInsuranceImageRequired" BOOLEAN, 
	"referenceLabId" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS ix_facilities_addr_city ON "Facilities" (("addressDetails" ->> 'city'));

CREATE INDEX IF NOT EXISTS ix_facilities_addr_state ON "Facilities" (("addressDetails" ->> 'state'));

CREATE TABLE IF NOT EXISTS "FacilityStaticData" (
	id SERIAL NOT NULL, 
	title VARCHAR, 
	value JSON[], 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "FacilityUsers" (
	id SERIAL NOT NULL, 
	"facilityId" INTEGER, 
	"userId" INTEGER, 
	"locationIds" INTEGER[], 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_FacilityUsers_facilityId" ON "FacilityUsers" ("facilityId");

CREATE INDEX IF NOT EXISTS "ix_FacilityUsers_userId" ON "FacilityUsers" ("userId");

CREATE TABLE IF NOT EXISTS "Guarantors" (
	id SERIAL NOT NULL, 
	"orderId" VARCHAR, 
	number VARCHAR, 
	"familyName" VARCHAR, 
	"givenName" VARCHAR, 
	"secondAndFurtherGivenName" VARCHAR, 
	"addressLine1" VARCHAR, 
	"addressLine2" VARCHAR, 
	city VARCHAR, 
	state VARCHAR, 
	zipcode VARCHAR, 
	"homePhone" VARCHAR, 
	"phoneNumberBusiness" VARCHAR, 
	"dateOfBirth" VARCHAR, 
	sex VARCHAR, 
	"relationshipIdentifier" VARCHAR, 
	"ssnNumber" VARCHAR, 
	"createdBy" INTEGER, 
	"updatedBy" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_Guarantors_orderId" ON "Guarantors" ("orderId");

CREATE TABLE IF NOT EXISTS "HelpSections" (
	id SERIAL NOT NULL, 
	sequence INTEGER, 
	title VARCHAR, 
	description TEXT, 
	attachments JSON, 
	"isActive" BOOLEAN, 
	"createdBy" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "IcdCodes" (
	id SERIAL NOT NULL, 
	"icdCode" VARCHAR, 
	description VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "Instruments" (
	id SERIAL NOT NULL, 
	instrument VARCHAR, 
	asset_number VARCHAR, 
	location VARCHAR, 
	manufacturer VARCHAR, 
	category VARCHAR, 
	model VARCHAR, 
	serial_number VARCHAR, 
	purchase_date TIMESTAMP WITH TIME ZONE, 
	last_calibration_date TIMESTAMP WITH TIME ZONE, 
	next_calibration_date TIMESTAMP WITH TIME ZONE, 
	calibration_frequency VARCHAR, 
	calibration_type VARCHAR, 
	vendor_name VARCHAR, 
	vendor_phone_number VARCHAR, 
	vendor_email_address VARCHAR, 
	created_by INTEGER, 
	"labId" INTEGER, 
	"isLinked" BOOLEAN, 
	"plateType" VARCHAR, 
	status VARCHAR, 
	attachments JSON, 
	"maintenanceLogs" JSON, 
	created_on TIMESTAMP WITH TIME ZONE, 
	updated_on TIMESTAMP WITH TIME ZONE, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "Insurers" (
	id SERIAL NOT NULL, 
	title VARCHAR, 
	code VARCHAR, 
	"payerId" VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "InventoryItems" (
	id SERIAL NOT NULL, 
	name VARCHAR, 
	type VARCHAR, 
	quantity INTEGER, 
	department INTEGER, 
	category VARCHAR, 
	units VARCHAR, 
	"storageLocation" VARCHAR, 
	"alertQuantity" INTEGER, 
	description TEXT, 
	"createdBy" INTEGER, 
	image JSON, 
	"isSubItems" BOOLEAN, 
	"isActive" BOOLEAN, 
	status VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "InventoryQuantities" (
	id SERIAL NOT NULL, 
	"subItemId" INTEGER, 
	"itemId" INTEGER, 
	"lotNumber" VARCHAR, 
	quantity INTEGER, 
	"expiaryDate" TIMESTAMP WITH TIME ZONE, 
	manufacturer VARCHAR, 
	batch VARCHAR, 
	catalog VARCHAR, 
	price VARCHAR, 
	"orderInfo" JSON, 
	event VARCHAR, 
	reason TEXT, 
	"isRemoved" BOOLEAN, 
	"createdBy" INTEGER, 
	"isUpdated" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_InventoryQuantities_itemId" ON "InventoryQuantities" ("itemId");

CREATE TABLE IF NOT EXISTS "InventoryStaticData" (
	id SERIAL NOT NULL, 
	title VARCHAR, 
	value JSON[], 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_InventoryStaticData_title" ON "InventoryStaticData" (title);

CREATE TABLE IF NOT EXISTS "InventorySubItems" (
	id SERIAL NOT NULL, 
	"inventoryItemId" INTEGER, 
	name VARCHAR, 
	units VARCHAR, 
	"alertQuantity" INTEGER, 
	description TEXT, 
	image JSON, 
	quantity INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_InventorySubItems_inventoryItemId" ON "InventorySubItems" ("inventoryItemId");

CREATE TABLE IF NOT EXISTS "LabImage" (
	id SERIAL NOT NULL, 
	"labId" INTEGER, 
	"attachmentName" VARCHAR, 
	"secureUrl" VARCHAR, 
	"mimeType" VARCHAR, 
	size INTEGER, 
	title VARCHAR, 
	"attachmentType" VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "LabOsBatchList" (
	id SERIAL NOT NULL, 
	"batchName" VARCHAR, 
	"worklistId" INTEGER, 
	"selectedSamples" INTEGER[], 
	"analyserIds" INTEGER[], 
	"testId" INTEGER, 
	"biomarkerId" INTEGER, 
	"reagentIds" INTEGER[], 
	"reagentLots" INTEGER[], 
	"labId" INTEGER, 
	"processingTechIds" INTEGER[], 
	"approvingTechIds" INTEGER[], 
	"createdBy" INTEGER, 
	"updatedBy" INTEGER, 
	"updatedOn" TIMESTAMP WITH TIME ZONE, 
	"createdOn" TIMESTAMP WITH TIME ZONE, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "LabOsCapa" (
	id SERIAL NOT NULL, 
	issue VARCHAR, 
	impact VARCHAR, 
	root_cause VARCHAR, 
	immediate_action VARCHAR, 
	preventative_action VARCHAR, 
	monitered VARCHAR, 
	attachment_urls JSON, 
	supervisor BOOLEAN, 
	comments TEXT, 
	created_by INTEGER, 
	lab_id INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "LabOsCategory" (
	id SERIAL NOT NULL, 
	"LabTypeCategory" VARCHAR, 
	"SubModules" VARCHAR[], 
	"Analysers" VARCHAR[], 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "LabOsControlMapping" (
	id SERIAL NOT NULL, 
	"runFileTargetName" VARCHAR, 
	"biomarkerId" INTEGER, 
	"testId" INTEGER, 
	"cutOffMin" INTEGER, 
	"cutOffMax" INTEGER, 
	control VARCHAR, 
	result VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "LabOsFiles" (
	id SERIAL NOT NULL, 
	department VARCHAR, 
	attachments JSON, 
	title VARCHAR, 
	"folderId" INTEGER, 
	"createdBy" INTEGER, 
	"updatedBy" INTEGER, 
	"isMarkForReview" BOOLEAN, 
	"isReviewed" BOOLEAN, 
	"reviewedBy" INTEGER, 
	"reviewedOn" TIMESTAMP WITH TIME ZONE, 
	"labId" INTEGER, 
	"serialCount" INTEGER, 
	"isDeleted" BOOLEAN, 
	"deletedBy" INTEGER, 
	"deletedOn" TIMESTAMP WITH TIME ZONE, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "LabOsFolders" (
	id SERIAL NOT NULL, 
	department VARCHAR, 
	name VARCHAR, 
	parent INTEGER, 
	"labId" INTEGER, 
	"serialCount" INTEGER, 
	"createdBy" INTEGER, 
	"isDeleted" BOOLEAN, 
	"deletedBy" INTEGER, 
	"deletedOn" TIMESTAMP WITH TIME ZONE, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "LabOsInventory" (
	id SERIAL NOT NULL, 
	inventory_category VARCHAR, 
	item_name VARCHAR, 
	item_type VARCHAR, 
	manufacturer VARCHAR, 
	catalog_number VARCHAR, 
	batch_number VARCHAR, 
	lot_number VARCHAR, 
	expiry_date TIMESTAMP WITH TIME ZONE, 
	stock_quantity VARCHAR, 
	stock_units VARCHAR, 
	alert_quantity VARCHAR, 
	storage_location VARCHAR, 
	qc_status VARCHAR, 
	event VARCHAR, 
	status VARCHAR, 
	department VARCHAR, 
	created_by INTEGER, 
	lab_id INTEGER, 
	created_on TIMESTAMP WITH TIME ZONE, 
	updated_on TIMESTAMP WITH TIME ZONE, 
	"childProduct" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "LabOsResultLogs" (
	id SERIAL NOT NULL, 
	"testId" INTEGER, 
	title VARCHAR, 
	"sampleJson" JSON, 
	status VARCHAR, 
	"plateNo" VARCHAR, 
	"createdBy" INTEGER, 
	"isCompleted" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "LabOsWorkList" (
	id SERIAL NOT NULL, 
	"worklistId" VARCHAR, 
	"createdBy" INTEGER, 
	"updatedBy" INTEGER, 
	"createdOn" TIMESTAMP WITH TIME ZONE, 
	"updatedOn" TIMESTAMP WITH TIME ZONE, 
	"assignedSamples" JSON, 
	"rerunSamples" VARCHAR[], 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "LabSessions" (
	id SERIAL NOT NULL, 
	step_id INTEGER, 
	sample_config JSON, 
	created_by INTEGER, 
	started_at TIMESTAMP WITH TIME ZONE, 
	completed_at TIMESTAMP WITH TIME ZONE, 
	rack_number VARCHAR, 
	status VARCHAR, 
	comments VARCHAR, 
	controls JSON, 
	workflow_id INTEGER, 
	sample_count INTEGER, 
	protocol_type VARCHAR, 
	lab_id INTEGER, 
	is_processed BOOLEAN, 
	"orderType" VARCHAR, 
	workflow_ids JSON, 
	step_ids JSON, 
	test_ids JSON, 
	panel_ids JSON, 
	panel_barcodes JSON, 
	selected_test_ids JSON, 
	processed_racks JSON, 
	samples_processed JSON, 
	sessions_processed INTEGER[], 
	is_extraction BOOLEAN, 
	is_hybrid BOOLEAN, 
	updated_by INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "LabStaticData" (
	id SERIAL NOT NULL, 
	title VARCHAR, 
	value JSON[], 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "LabUsers" (
	id SERIAL NOT NULL, 
	"labId" INTEGER, 
	"userId" INTEGER, 
	"locationIds" INTEGER[], 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_LabUsers_labId" ON "LabUsers" ("labId");

CREATE INDEX IF NOT EXISTS "ix_LabUsers_userId" ON "LabUsers" ("userId");

CREATE TABLE IF NOT EXISTS "Labs" (
	id SERIAL NOT NULL, 
	name VARCHAR, 
	code VARCHAR, 
	"labExternalId" VARCHAR, 
	"npiNumber" VARCHAR, 
	"cliaId" VARCHAR, 
	"capId" VARCHAR, 
	"colaId" VARCHAR, 
	"labType" VARCHAR, 
	"isSdiLab" BOOLEAN, 
	"isActive" BOOLEAN, 
	"emailId" VARCHAR, 
	status VARCHAR, 
	"mobileNumber" VARCHAR, 
	"secondaryMobileNumber" VARCHAR, 
	"faxNumber" VARCHAR, 
	"addressLine1" VARCHAR, 
	"addressLine2" VARCHAR, 
	zipcode VARCHAR, 
	state VARCHAR, 
	city VARCHAR, 
	"adminId" INTEGER, 
	"createdBy" INTEGER, 
	logo JSON, 
	"themeColor" VARCHAR, 
	"directorDetails" JSON, 
	"primaryContact" JSON, 
	"lastCompletedStep" INTEGER, 
	"labRole" VARCHAR, 
	"referenceFacilityId" INTEGER, 
	"referenceLocationId" INTEGER, 
	attachments JSON, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "LinkLabBiomarker" (
	id SERIAL NOT NULL, 
	"labId" INTEGER, 
	"biomarkerId" INTEGER, 
	"isActive" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "LinkLabPanel" (
	id SERIAL NOT NULL, 
	"labId" INTEGER, 
	"panelId" INTEGER, 
	"isActive" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "LinkLabTest" (
	id SERIAL NOT NULL, 
	"labId" INTEGER, 
	"testId" INTEGER, 
	"isActive" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "LinkLocationBiomarker" (
	id SERIAL NOT NULL, 
	"locationId" INTEGER, 
	"biomarkerId" INTEGER, 
	"isActive" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "LinkLocationPanel" (
	id SERIAL NOT NULL, 
	"locationId" INTEGER, 
	"panelId" INTEGER, 
	"isActive" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "LinkLocationTest" (
	id SERIAL NOT NULL, 
	"locationId" INTEGER, 
	"testId" INTEGER, 
	"isActive" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "LinkPatientLocation" (
	id SERIAL NOT NULL, 
	"locationId" INTEGER, 
	"patientId" INTEGER, 
	"facilityId" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "LocationFavoriteIcdCode" (
	id SERIAL NOT NULL, 
	"locationId" INTEGER, 
	"icdCodeId" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "LocationPhysicians" (
	id SERIAL NOT NULL, 
	"locationId" INTEGER, 
	"physicianId" INTEGER, 
	"isActive" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_LocationPhysicians_locationId" ON "LocationPhysicians" ("locationId");

CREATE INDEX IF NOT EXISTS "ix_LocationPhysicians_physicianId" ON "LocationPhysicians" ("physicianId");

CREATE TABLE IF NOT EXISTS "LocationUsers" (
	id SERIAL NOT NULL, 
	"locationId" INTEGER, 
	"userId" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_LocationUsers_locationId" ON "LocationUsers" ("locationId");

CREATE INDEX IF NOT EXISTS "ix_LocationUsers_userId" ON "LocationUsers" ("userId");

CREATE TABLE IF NOT EXISTS "Locations" (
	id SERIAL NOT NULL, 
	"facilityId" INTEGER, 
	name VARCHAR, 
	type VARCHAR, 
	code VARCHAR, 
	"adminId" INTEGER, 
	"addressDetails" JSON, 
	"primaryContactDetails" JSON, 
	"criticalDetails" JSON, 
	"billingDetails" JSON, 
	"emergencyContactDetails" JSON[], 
	"accountPreferences" JSON, 
	"labId" INTEGER, 
	"bloodDrawInformation" JSON, 
	panels INTEGER[], 
	"createdBy" INTEGER, 
	status VARCHAR, 
	"isActive" BOOLEAN, 
	"internalLocationId" VARCHAR, 
	purpose VARCHAR, 
	"lastCompletedStep" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_Locations_facilityId" ON "Locations" ("facilityId");

CREATE INDEX IF NOT EXISTS ix_locations_addr_city ON "Locations" (("addressDetails" ->> 'city'));

CREATE INDEX IF NOT EXISTS ix_locations_addr_state ON "Locations" (("addressDetails" ->> 'state'));

CREATE TABLE IF NOT EXISTS "Medication" (
	id SERIAL NOT NULL, 
	"brandName" TEXT, 
	"genericName" TEXT, 
	"dosageForm" TEXT, 
	dosage TEXT, 
	unit TEXT, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "Notifications" (
	id SERIAL NOT NULL, 
	"fromUserId" INTEGER, 
	"toUserId" INTEGER, 
	message VARCHAR, 
	title VARCHAR, 
	url VARCHAR, 
	"isActive" BOOLEAN, 
	"createdBy" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_Notifications_toUserId" ON "Notifications" ("toUserId");

CREATE TABLE IF NOT EXISTS "OCRCompanies" (
	id SERIAL NOT NULL, 
	image JSON, 
	"companyName" VARCHAR, 
	config JSON, 
	"addedBy" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "OCREOBBatch" (
	id SERIAL NOT NULL, 
	name VARCHAR, 
	status VARCHAR, 
	"numberOfFiles" INTEGER, 
	"createdBy" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "OCREOBBatchSession" (
	id SERIAL NOT NULL, 
	"batchId" INTEGER, 
	"filePath" VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	status VARCHAR, 
	"numberOfFiles" INTEGER, 
	"createdBy" INTEGER, 
	filename VARCHAR, 
	"isProcessed" BOOLEAN, 
	mimetype VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "OCREOBBatchSessionImages" (
	id SERIAL NOT NULL, 
	"batchId" INTEGER, 
	"sessionId" INTEGER, 
	"filePath" VARCHAR, 
	filename VARCHAR, 
	"companyName" VARCHAR, 
	"isSpam" BOOLEAN, 
	"isProcessed" BOOLEAN, 
	status VARCHAR, 
	"createdBy" INTEGER, 
	mimetype VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "OCREOBBatchSessionResults" (
	id SERIAL NOT NULL, 
	"batchId" INTEGER, 
	"filePath" VARCHAR, 
	filename VARCHAR, 
	mimetype VARCHAR, 
	"sessionId" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "OCRInferenceSession" (
	id SERIAL NOT NULL, 
	"numberOfInferenceFiles" INTEGER, 
	"numberOfFiles" INTEGER, 
	"uploadedBy" INTEGER, 
	status VARCHAR, 
	name VARCHAR, 
	comments VARCHAR, 
	"modeOfUpload" VARCHAR, 
	"metaDataOfSource" JSON, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "OCRInferenceSessionImage" (
	id SERIAL NOT NULL, 
	"fileName" VARCHAR, 
	"secureUrl" VARCHAR, 
	mimetype VARCHAR, 
	"uploadedBy" INTEGER, 
	"inferenceSessionId" INTEGER, 
	results JSON, 
	"companyName" VARCHAR, 
	"ocrResponse" JSON, 
	config JSON, 
	status VARCHAR, 
	"isInferenceCompleted" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "OCRSettings" (
	id SERIAL NOT NULL, 
	title VARCHAR, 
	code VARCHAR, 
	"addedBy" NUMERIC, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "OCRUser" (
	id SERIAL NOT NULL, 
	name VARCHAR, 
	"secreteKey" VARCHAR, 
	token TEXT, 
	expiry JSON, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "OrderAttachment" (
	id SERIAL NOT NULL, 
	"orderId" INTEGER, 
	"sampleId" INTEGER, 
	"attachmentType" VARCHAR, 
	title VARCHAR, 
	"secureUrl" VARCHAR, 
	"mimeType" VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "OrderExternalIds" (
	id SERIAL NOT NULL, 
	"orderId" INTEGER, 
	"serviceName" VARCHAR, 
	"externalId" VARCHAR, 
	"isActive" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "OrderFlag" (
	id SERIAL NOT NULL, 
	"orderId" INTEGER, 
	"resultReportedToInterface" BOOLEAN, 
	"isArkstoneReportRequired" BOOLEAN, 
	"isArkstoneReportGenerated" BOOLEAN, 
	"isEmgenexReportRequired" BOOLEAN, 
	"isEmgenexReportGenerated" BOOLEAN, 
	"isChoicePharmDReportRequired" BOOLEAN, 
	"isChoicePharmDReportGenerated" BOOLEAN, 
	"isDrChronoSyncRequired" BOOLEAN, 
	"isDrChronoOrderCreated" BOOLEAN, 
	"isDrChronoOrderResultSubmitted" BOOLEAN, 
	"createdBy" INTEGER, 
	"updatedBy" INTEGER, 
	"createdAt" JSON, 
	"updatedAt" JSON, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "OrderFlagV2" (
	id SERIAL NOT NULL, 
	"resultReportedToInterface" BOOLEAN, 
	"orderId" INTEGER, 
	"reportingService" VARCHAR, 
	"isReportGenerated" BOOLEAN, 
	"createdBy" INTEGER, 
	"updatedBy" INTEGER, 
	"createdAt" JSON, 
	"updatedAt" JSON, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "OrderReportHeaders" (
	id SERIAL NOT NULL, 
	"triggerType" VARCHAR, 
	name VARCHAR, 
	layout VARCHAR, 
	"testIds" INTEGER[], 
	"createdBy" INTEGER, 
	"isActive" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "OrderResults" (
	id SERIAL NOT NULL, 
	"orderId" INTEGER, 
	"sampleId" INTEGER, 
	"pdfGeneratedDate" VARCHAR, 
	"pdfDetails" JSON, 
	results JSON, 
	"loginUserId" INTEGER, 
	"resultedMode" VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_OrderResults_orderId" ON "OrderResults" ("orderId");

CREATE INDEX IF NOT EXISTS "ix_OrderResults_sampleId" ON "OrderResults" ("sampleId");

CREATE TABLE IF NOT EXISTS "OrderSampleGrouping" (
	id SERIAL NOT NULL, 
	"orderId" INTEGER, 
	"orderType" VARCHAR, 
	"panelId" INTEGER, 
	"testId" INTEGER, 
	"biomarkerId" INTEGER, 
	"pdfDetails" JSON, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "OrderSamples" (
	id SERIAL NOT NULL, 
	"sampleCode" VARCHAR, 
	"orderId" INTEGER, 
	"orderDetails" JSON, 
	"panelId" INTEGER, 
	"panelDetails" JSON, 
	"physicianId" INTEGER, 
	"physicianDetails" JSON, 
	"sampleType" VARCHAR, 
	"billingMode" VARCHAR, 
	"externalReferenceNumber" VARCHAR, 
	"insuranceDetails" JSON, 
	"rejectionDetails" JSON, 
	status VARCHAR, 
	"resultedMode" VARCHAR, 
	"isIntakeFormCompleted" BOOLEAN, 
	"isSubmitted" BOOLEAN, 
	"isConsentSigned" BOOLEAN, 
	"isEnbChecked" BOOLEAN, 
	"isSendOut" BOOLEAN, 
	"sendOutLabDetails" JSON, 
	"icdCodes" VARCHAR[], 
	"icdCodeDetails" JSON[], 
	"dateOfCollection" VARCHAR, 
	"timeOfCollection" VARCHAR, 
	"dateTimeOfCollection" VARCHAR, 
	"isPriorityOrder" BOOLEAN, 
	"isPaymentCompleted" BOOLEAN, 
	"typeOfBarcode" VARCHAR, 
	barcode VARCHAR, 
	"patientBarcode" VARCHAR, 
	"labBarcode" VARCHAR, 
	"isBarcodeReplaced" BOOLEAN, 
	"isAccessioned" BOOLEAN, 
	"isStateReported" BOOLEAN, 
	"statusTimeLine" JSON[], 
	"createdBy" INTEGER, 
	"accessionedBy" INTEGER, 
	"accessionedLabId" INTEGER, 
	"isPdfGenerated" BOOLEAN, 
	"pdfGeneratedDate" VARCHAR, 
	"resultSentToPatient" BOOLEAN, 
	"accessionedDate" VARCHAR, 
	"pdfDetails" JSON, 
	results JSON, 
	source VARCHAR, 
	"testId" INTEGER, 
	"testDetails" JSON, 
	"biomarkerId" INTEGER, 
	"biomarkerDetails" JSON, 
	"isPanel" BOOLEAN, 
	"orderType" VARCHAR, 
	"orderSampleGroupingId" INTEGER, 
	"receivedDate" VARCHAR, 
	"receivedTime" VARCHAR, 
	"receivedDateTime" VARCHAR, 
	"proposedDateOfCollection" VARCHAR, 
	"proposedTimeOfCollection" VARCHAR, 
	"proposedDateTimeOfCollection" VARCHAR, 
	"priorityOrderStatus" VARCHAR, 
	"createdByDetails" JSON, 
	"accessionedDetails" JSON, 
	"accessionedLabDetails" JSON, 
	"sampleCreatedTime" JSON, 
	"reasonForVisit" VARCHAR, 
	"advancedMDSyncStatus" VARCHAR, 
	"advancedMDSyncDetails" JSON, 
	"primaryInsurance" JSON, 
	"secondaryInsurance" JSON, 
	"tertiaryInsurance" JSON, 
	notes TEXT, 
	"cptCodes" VARCHAR[], 
	"cptCodeDetails" JSON[], 
	"medicationDetails" JSON[], 
	"sampleResultObj" JSON, 
	"trackingId" VARCHAR, 
	"isPocTest" BOOLEAN, 
	"isReflexTest" BOOLEAN, 
	"sampleBarcodeId" VARCHAR, 
	"isFlagged" BOOLEAN, 
	worklistid INTEGER, 
	"labOsBatchId" INTEGER, 
	"linkedSampleId" INTEGER, 
	"primarySampleId" INTEGER, 
	"isLinkedSample" BOOLEAN, 
	"linkedTestResults" JSON, 
	"isSupplementSample" BOOLEAN, 
	"updatedReportData" JSON, 
	"isLatestReportGenerated" BOOLEAN, 
	"isReportAmended" BOOLEAN, 
	"isResultCorrected" BOOLEAN, 
	"latestPdfGeneratedDate" VARCHAR, 
	"isSamePdf" BOOLEAN, 
	"swabSite" VARCHAR, 
	"internalStatus" VARCHAR, 
	"isBasicDetailsFilled" BOOLEAN, 
	"consentDetails" JSON, 
	"enableAlert" BOOLEAN, 
	"intakeFromCompletionTime" JSON, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_OrderSamples_orderId" ON "OrderSamples" ("orderId");

CREATE INDEX IF NOT EXISTS "ix_OrderSamples_sampleCode" ON "OrderSamples" ("sampleCode");

CREATE TABLE IF NOT EXISTS "OrderStaticData" (
	id SERIAL NOT NULL, 
	title VARCHAR, 
	value JSON[], 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "Orders" (
	id SERIAL NOT NULL, 
	code VARCHAR, 
	"facilityId" INTEGER, 
	"locationId" INTEGER, 
	"facilityDetails" JSON, 
	"locationDetails" JSON, 
	"patientId" INTEGER, 
	"externalPatientId" VARCHAR, 
	"externalOrderId" VARCHAR, 
	"patientDetails" JSON, 
	status VARCHAR, 
	"numberOfSamplesOrdered" INTEGER, 
	"numberOfSamplesResulted" INTEGER, 
	"physicianId" INTEGER, 
	"physicianDetails" JSON, 
	"labDetails" JSON, 
	"isPriorityOrder" BOOLEAN, 
	"isConsentSigned" BOOLEAN, 
	"createdBy" INTEGER, 
	"createdByDetails" JSON, 
	source VARCHAR, 
	"orderPlacedTime" VARCHAR, 
	attachments JSON, 
	"labId" INTEGER, 
	"primaryInsuranceId" INTEGER, 
	"secondaryInsuranceId" INTEGER, 
	"tertiaryInsuranceId" INTEGER, 
	"billingMode" VARCHAR, 
	"icdCodes" VARCHAR[], 
	"icdCodeDetails" JSON[], 
	allergies VARCHAR[], 
	"allergieIds" INTEGER[], 
	"medicationDetails" JSON[], 
	"integrationDetails" JSON, 
	"internalOrderId" VARCHAR, 
	"rejectionDetails" JSON, 
	"rawOrderResultData" JSON, 
	"priorityOrderStatus" VARCHAR, 
	"resultSentToPatient" BOOLEAN, 
	"externalReferenceNumber" VARCHAR, 
	"sampleDraftDetails" JSON, 
	"isDiscarded" BOOLEAN, 
	"testOrderReportTitle" VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_Orders_code" ON "Orders" (code);

CREATE INDEX IF NOT EXISTS "ix_Orders_patientId" ON "Orders" ("patientId");

CREATE TABLE IF NOT EXISTS "PanelIcdCode" (
	id SERIAL NOT NULL, 
	"panelId" INTEGER, 
	"icdCode" VARCHAR, 
	description VARCHAR, 
	"linkedToLocationId" INTEGER, 
	"createdBy" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "PanelImage" (
	id SERIAL NOT NULL, 
	"panelId" INTEGER, 
	"attachmentName" VARCHAR, 
	"secureUrl" VARCHAR, 
	"mimeType" VARCHAR, 
	size INTEGER, 
	title VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "PanelStaticData" (
	id SERIAL NOT NULL, 
	title VARCHAR, 
	value JSON[], 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "PanelVariableTemplate" (
	id SERIAL NOT NULL, 
	"panelId" INTEGER, 
	"templateName" VARCHAR, 
	"mimeType" VARCHAR, 
	"securePath" VARCHAR, 
	"isActive" BOOLEAN, 
	"isDelete" BOOLEAN, 
	"createdBy" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "Panels" (
	id SERIAL NOT NULL, 
	name VARCHAR, 
	code VARCHAR, 
	"testIds" INTEGER[], 
	description TEXT, 
	"isActive" BOOLEAN, 
	status VARCHAR, 
	"createdBy" INTEGER, 
	"sampleType" VARCHAR, 
	"biomarkerIds" INTEGER[], 
	"internalPanelId" VARCHAR, 
	"hasOrderingLimit" BOOLEAN, 
	"alertLimit" INTEGER, 
	"maxLimit" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "PatientAttachments" (
	id SERIAL NOT NULL, 
	"patientId" INTEGER, 
	title VARCHAR, 
	"secureUrl" VARCHAR, 
	"mimeType" VARCHAR, 
	"attachmentType" VARCHAR, 
	"attachmentName" VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "PatientExternalIds" (
	id SERIAL NOT NULL, 
	"patientId" INTEGER, 
	"serviceName" VARCHAR, 
	"externalId" VARCHAR, 
	"isActive" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "PatientInsurances" (
	id SERIAL NOT NULL, 
	"patientId" INTEGER, 
	"firstName" VARCHAR, 
	"middleName" VARCHAR, 
	"lastName" VARCHAR, 
	"dateOfBirth" VARCHAR, 
	"payerId" VARCHAR, 
	type VARCHAR, 
	"insuranceCompany" VARCHAR, 
	"insurancePlan" VARCHAR, 
	"policyNumber" VARCHAR, 
	relationship VARCHAR, 
	"networkPlanName" VARCHAR, 
	"groupName" VARCHAR, 
	"groupNetwork" VARCHAR, 
	"effectiveDate" VARCHAR, 
	"ipaMedicalGroupName" VARCHAR, 
	"groupId" VARCHAR, 
	"isSameName" BOOLEAN, 
	"frontImage" JSON, 
	"backImage" JSON, 
	"clearingHouse" VARCHAR, 
	"clearingHouseCode" VARCHAR, 
	"clearingHouseId" INTEGER, 
	"clearingHouseInsuranceId" INTEGER, 
	"CPID" VARCHAR, 
	"enbotDetails" JSON, 
	"isEnbotChecked" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_PatientInsurances_patientId" ON "PatientInsurances" ("patientId");

CREATE TABLE IF NOT EXISTS "PatientIntakeResponse" (
	id SERIAL NOT NULL, 
	"patientId" INTEGER, 
	"responseWithCode" JSON, 
	source VARCHAR, 
	"startTime" JSON, 
	"orderId" INTEGER, 
	"sampleId" INTEGER, 
	"formId" INTEGER, 
	"sessionId" VARCHAR, 
	"isCompleted" BOOLEAN, 
	"shouldNotify" BOOLEAN, 
	"mlResponse" JSON, 
	"mlPayload" JSON, 
	"responseWithQuestion" JSON, 
	"endTime" JSON, 
	"testId" INTEGER, 
	"mlResponseTime" VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "PatientStaticData" (
	id SERIAL NOT NULL, 
	title VARCHAR, 
	value JSON[], 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "PatientToken" (
	id SERIAL NOT NULL, 
	"patientId" INTEGER, 
	token TEXT, 
	"expiryDate" VARCHAR, 
	"isActive" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "PatientVisits" (
	id SERIAL NOT NULL, 
	"orderId" INTEGER, 
	"attendingDoctorId" INTEGER, 
	"attendingDoctorFamilyName" VARCHAR, 
	"attendingDoctorGivenName" VARCHAR, 
	"attendingDoctorSecondAndFurtherGivenName" VARCHAR, 
	"attendingDoctorDegree" VARCHAR, 
	"referringDoctorId" INTEGER, 
	"referringDoctorFamilyName" VARCHAR, 
	"referringDoctorGivenName" VARCHAR, 
	"referringDoctorSecondAndFurtherGivenName" VARCHAR, 
	"referringDoctorDegree" VARCHAR, 
	"hospitalService" VARCHAR, 
	"patientType" VARCHAR, 
	"visitNumberId" VARCHAR, 
	"financialClass" VARCHAR, 
	"admitDateTime" VARCHAR, 
	"dischargeDateTime" VARCHAR, 
	"createdBy" INTEGER, 
	"updatedBy" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_PatientVisits_orderId" ON "PatientVisits" ("orderId");

CREATE TABLE IF NOT EXISTS "Patients" (
	id SERIAL NOT NULL, 
	"firstName" VARCHAR, 
	"middleName" VARCHAR, 
	"lastName" VARCHAR, 
	"dateOfBirth" VARCHAR, 
	"mobileNumber" VARCHAR, 
	"mobileNumberCode" VARCHAR, 
	code VARCHAR, 
	"isMobileNumberVerified" BOOLEAN, 
	gender VARCHAR, 
	ethnicity VARCHAR, 
	race VARCHAR, 
	"secondaryMobileNumber" VARCHAR, 
	"secondaryMobileNumberCode" VARCHAR, 
	"businessEmailId" VARCHAR, 
	"businessMobileNumber" VARCHAR, 
	"emailId" VARCHAR, 
	"addressLine1" VARCHAR, 
	"addressLine2" VARCHAR, 
	zipcode VARCHAR, 
	state VARCHAR, 
	city VARCHAR, 
	county VARCHAR, 
	country VARCHAR, 
	prefix VARCHAR, 
	suffix VARCHAR, 
	"aliasName" VARCHAR, 
	"patientAccountNumber" VARCHAR, 
	ssn VARCHAR, 
	nationality VARCHAR, 
	"maritalStatus" VARCHAR, 
	degree VARCHAR, 
	notes VARCHAR, 
	"isDrivingLicenseAvailable" BOOLEAN, 
	"drivingLicenseNumber" VARCHAR, 
	"isPatientDead" BOOLEAN, 
	"timeOfDeath" VARCHAR, 
	"dateOfDeath" VARCHAR, 
	password VARCHAR, 
	"heightInInches" FLOAT, 
	"heightInFeet" FLOAT, 
	"heightInCms" FLOAT, 
	weight FLOAT, 
	"externalPatientId" VARCHAR, 
	"externalOrderId" VARCHAR, 
	"parentAccountId" INTEGER, 
	"specialPatientType" VARCHAR, 
	"isPasswordSet" BOOLEAN, 
	"isSelfRegistered" BOOLEAN, 
	"isSpecialPatient" BOOLEAN, 
	source VARCHAR, 
	"isInsuranceAvailable" BOOLEAN, 
	"isActive" BOOLEAN, 
	"isDeleted" BOOLEAN, 
	"createdBy" INTEGER, 
	"AMDPatientId" VARCHAR, 
	"internalPatientId" VARCHAR, 
	"allergieIds" INTEGER[], 
	"patientId1" VARCHAR, 
	"patientId2" VARCHAR, 
	"patientId3" VARCHAR, 
	"alternateId1" VARCHAR, 
	"alternateId2" VARCHAR, 
	"assignedBy1" VARCHAR, 
	"assignedBy2" VARCHAR, 
	"assignedBy3" VARCHAR, 
	"customField1" VARCHAR, 
	"customField2" VARCHAR, 
	"customField3" VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_Patients_code" ON "Patients" (code);

CREATE INDEX IF NOT EXISTS "ix_Patients_emailId" ON "Patients" ("emailId");

CREATE TABLE IF NOT EXISTS "Plates" (
	id SERIAL NOT NULL, 
	department INTEGER, 
	equipment INTEGER, 
	plate_name VARCHAR, 
	rows VARCHAR, 
	row_indication_type VARCHAR, 
	columns VARCHAR, 
	column_indication_type VARCHAR, 
	is_controls_available BOOLEAN, 
	controls JSON, 
	created_by INTEGER, 
	updated_on TIMESTAMP WITH TIME ZONE, 
	lab_id INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "ProductCart" (
	id SERIAL NOT NULL, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "ProductImages" (
	id SERIAL NOT NULL, 
	"productId" INTEGER, 
	"mimeType" VARCHAR, 
	"secureUrl" VARCHAR, 
	"fileName" VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_ProductImages_productId" ON "ProductImages" ("productId");

CREATE TABLE IF NOT EXISTS "ProductQuantity" (
	id SERIAL NOT NULL, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "ProductQuantityLog" (
	id SERIAL NOT NULL, 
	"productId" INTEGER, 
	value INTEGER, 
	"updatedValue" INTEGER, 
	"addedBy" INTEGER, 
	operation VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "Products" (
	id SERIAL NOT NULL, 
	name VARCHAR, 
	"panelId" INTEGER, 
	"productCode" VARCHAR, 
	quantity INTEGER, 
	"alertLevelStock" INTEGER, 
	description VARCHAR, 
	"tagLine" VARCHAR, 
	"methodOfCollection" VARCHAR, 
	"resultingDays" VARCHAR, 
	analytes VARCHAR[], 
	price INTEGER, 
	"isActive" BOOLEAN, 
	"isDeleted" BOOLEAN, 
	"addedBy" INTEGER, 
	"productCatalogLink" VARCHAR, 
	"lastBarcodeValue" INTEGER, 
	"lastUpdatedBy" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "QrCodes" (
	id SERIAL NOT NULL, 
	code VARCHAR, 
	"qrData" VARCHAR, 
	"facilityId" INTEGER, 
	"locationId" INTEGER, 
	"panelId" INTEGER, 
	"physicianId" INTEGER, 
	"createdBy" INTEGER, 
	"isActive" BOOLEAN, 
	type VARCHAR, 
	flow VARCHAR, 
	caption TEXT, 
	"imageDetails" JSON, 
	"billingMode" VARCHAR, 
	"expiryTime" VARCHAR, 
	"isIntakeFormAvailable" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_QrCodes_code" ON "QrCodes" (code);

CREATE TABLE IF NOT EXISTS "Question" (
	id SERIAL NOT NULL, 
	title VARCHAR, 
	code VARCHAR, 
	"subTitle" VARCHAR, 
	"showLabel" BOOLEAN, 
	"formControlType" VARCHAR, 
	"formControlSize" VARCHAR, 
	"placeHolder" VARCHAR, 
	mlref VARCHAR, 
	options JSON[], 
	"isSubQuestion" BOOLEAN, 
	"isMultiSelection" BOOLEAN, 
	"isHorizontalAlign" BOOLEAN, 
	"isHavingNoneOption" BOOLEAN, 
	"isRequired" BOOLEAN, 
	"isConditional" BOOLEAN, 
	"conditionRules" JSON[], 
	"isActive" BOOLEAN, 
	"autoHeight" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "QuestionForm" (
	id SERIAL NOT NULL, 
	title VARCHAR, 
	descriptions VARCHAR, 
	steps JSON[], 
	"isActive" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "QuestionFormStep" (
	id SERIAL NOT NULL, 
	title VARCHAR, 
	descriptions VARCHAR, 
	"assetUrl" VARCHAR, 
	"toolTip" TEXT, 
	"canNavigateBack" BOOLEAN, 
	"proceedButtonText" VARCHAR, 
	"canSkipTheStep" BOOLEAN, 
	"isActive" BOOLEAN, 
	questions INTEGER[], 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "Reagents" (
	id SERIAL NOT NULL, 
	name VARCHAR, 
	code VARCHAR, 
	inventory_category VARCHAR, 
	type VARCHAR, 
	manufacturer VARCHAR, 
	"labId" INTEGER, 
	"createdBy" INTEGER, 
	"isActive" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "ReportArchive" (
	id SERIAL NOT NULL, 
	"sampleId" INTEGER, 
	"updateReason" VARCHAR, 
	"updateType" VARCHAR, 
	"accessionId" VARCHAR, 
	"pdfDetails" JSON, 
	"updatedFields" JSON, 
	"resultVersion" INTEGER, 
	"reportVersion" INTEGER, 
	"updatedBy" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "ResultControlComment" (
	id SERIAL NOT NULL, 
	"uploadResultSessionId" INTEGER, 
	"testPanelCode" VARCHAR, 
	"resultControlId" INTEGER, 
	"createdBy" INTEGER, 
	"isCls" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "ResultControls" (
	id SERIAL NOT NULL, 
	"uploadResultSessionId" INTEGER, 
	"testPanelCode" VARCHAR, 
	"wellPosition" VARCHAR, 
	control VARCHAR, 
	"targetName" VARCHAR, 
	"biomarkerName" VARCHAR, 
	fluorophore VARCHAR, 
	"ctValue" FLOAT, 
	result VARCHAR, 
	comments TEXT, 
	"reasonForChange" TEXT, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_ResultControls_uploadResultSessionId" ON "ResultControls" ("uploadResultSessionId");

CREATE TABLE IF NOT EXISTS "ResultSampleComment" (
	id SERIAL NOT NULL, 
	"resultSampleId" INTEGER, 
	"createdBy" INTEGER, 
	"isCls" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "ResultSampleDetail" (
	id SERIAL NOT NULL, 
	"resultSampleId" INTEGER, 
	"wellPosition" VARCHAR, 
	"accessionId" VARCHAR, 
	"targetName" VARCHAR, 
	"biomarkerId" INTEGER, 
	"biomarkerName" VARCHAR, 
	fluorophore VARCHAR, 
	"ctValue" FLOAT, 
	"cutoffValue" FLOAT, 
	"cutoffCycle" FLOAT, 
	result VARCHAR, 
	"isQuantitative" BOOLEAN, 
	gender VARCHAR, 
	age INTEGER, 
	value1 VARCHAR, 
	expression VARCHAR, 
	value2 VARCHAR, 
	units VARCHAR, 
	notes TEXT, 
	color VARCHAR, 
	"reasonForChange" TEXT, 
	"isOutOfRange" BOOLEAN, 
	version INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "ResultSampleMetaDetails" (
	id SERIAL NOT NULL, 
	"resultSampleId" INTEGER, 
	"accessionId" VARCHAR, 
	version INTEGER, 
	"sampleId" INTEGER, 
	"orderId" INTEGER, 
	"patientFirstName" VARCHAR, 
	"patientMiddleName" VARCHAR, 
	"patientLastName" VARCHAR, 
	"patientPrefix" VARCHAR, 
	"patientSuffix" VARCHAR, 
	"patientGender" VARCHAR, 
	"patientDOB" VARCHAR, 
	"patientEmail" VARCHAR, 
	"reasonForAmendment" VARCHAR, 
	"reasonForCorrection" VARCHAR, 
	"addedBy" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "ResultSamples" (
	id SERIAL NOT NULL, 
	"uploadResultSessionId" INTEGER, 
	"accessionId" VARCHAR, 
	"sampleId" INTEGER, 
	"orderId" INTEGER, 
	"isGenerated" BOOLEAN, 
	"testCode" VARCHAR, 
	"biomarkerCode" VARCHAR, 
	"targetName" VARCHAR, 
	"biomarkerName" VARCHAR, 
	fluorophore VARCHAR, 
	"wellPosition" VARCHAR, 
	"cqValue" FLOAT, 
	result VARCHAR, 
	value VARCHAR, 
	"isMarkForReview" BOOLEAN, 
	"reasonForRejection" TEXT, 
	"isManual" BOOLEAN, 
	"isRejected" BOOLEAN, 
	"isValid" BOOLEAN, 
	"isRerun" BOOLEAN, 
	comments TEXT, 
	note TEXT, 
	"pdfVariable" JSON, 
	"reviewerNote" TEXT, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_ResultSamples_orderId" ON "ResultSamples" ("orderId");

CREATE INDEX IF NOT EXISTS "ix_ResultSamples_sampleId" ON "ResultSamples" ("sampleId");

CREATE INDEX IF NOT EXISTS "ix_ResultSamples_uploadResultSessionId" ON "ResultSamples" ("uploadResultSessionId");

CREATE TABLE IF NOT EXISTS "ResultSession" (
	id SERIAL NOT NULL, 
	"testId" INTEGER, 
	"testDetails" JSON, 
	"createdBy" VARCHAR, 
	"createdByDetails" JSON, 
	"numberOfSamples" INTEGER, 
	"numberOfSamplesMatched" INTEGER, 
	"numberOfSamplesUnMatched" INTEGER, 
	"isGenerateRequestSubmitted" BOOLEAN, 
	"attachmentDetails" JSON, 
	timezone VARCHAR, 
	"biomarkerId" INTEGER, 
	"biomarkerDetails" JSON, 
	"reportId" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "ResultSessionValue" (
	id SERIAL NOT NULL, 
	"sessionId" INTEGER, 
	results JSON, 
	"sampleDetails" JSON, 
	"orderDetails" JSON, 
	"pdfDetails" JSON, 
	"isPdfGenerated" BOOLEAN, 
	"isResultMatched" BOOLEAN, 
	"testId" INTEGER, 
	"testDetails" JSON, 
	"biomarkerId" INTEGER, 
	"biomarkerDetails" JSON, 
	"pdfJsonDetails" JSON, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "ReviewResult" (
	id SERIAL NOT NULL, 
	"uploadResultSessionId" INTEGER, 
	"resultSampleIds" JSON, 
	"reviewedBy" INTEGER, 
	"accessionIds" JSON, 
	"reviewNote" VARCHAR, 
	"isDiscarded" BOOLEAN, 
	"discardedReason" VARCHAR, 
	"discardedBy" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "RoleAclModels" (
	id SERIAL NOT NULL, 
	"roleId" INTEGER, 
	"moduleAccess" VARCHAR, 
	"featureAccess" VARCHAR, 
	"apiAccess" VARCHAR[], 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_RoleAclModels_roleId" ON "RoleAclModels" ("roleId");

CREATE TABLE IF NOT EXISTS "Roles" (
	id SERIAL NOT NULL, 
	title VARCHAR, 
	code VARCHAR, 
	"isSdiRole" BOOLEAN, 
	"isSignatureRequired" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "SampleProcessingPlate" (
	id SERIAL NOT NULL, 
	"sessionId" INTEGER, 
	"column" VARCHAR, 
	row VARCHAR, 
	value VARCHAR, 
	"testOrPanelId" INTEGER, 
	"testOrPanelType" VARCHAR, 
	"testOrPanelCode" VARCHAR, 
	"testOrPanelName" VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "SampleProcessingSession" (
	id SERIAL NOT NULL, 
	department VARCHAR, 
	"processingType" VARCHAR, 
	"worklistIds" JSON, 
	"subListIds" JSON, 
	"plateId" VARCHAR, 
	comments VARCHAR, 
	"plateType" VARCHAR, 
	rows INTEGER, 
	columns INTEGER, 
	"createdBy" INTEGER, 
	status VARCHAR, 
	"isDiscarded" BOOLEAN, 
	"lastDiscardedBy" INTEGER, 
	"isExisting" BOOLEAN, 
	"existingIds" JSON, 
	"isUploadFile" BOOLEAN, 
	"uploadFileDetails" JSON, 
	"sampleIds" JSON, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "SendOutOrderResult" (
	id SERIAL NOT NULL, 
	"accessionId" VARCHAR, 
	"orderId" INTEGER, 
	"biomarkerId" INTEGER, 
	"testId" INTEGER, 
	result VARCHAR, 
	version INTEGER, 
	"biomarkerResultedAt" VARCHAR, 
	flag VARCHAR, 
	"addedBy" INTEGER, 
	"resultRemarks" VARCHAR, 
	"isResultAvailable" BOOLEAN, 
	"microbialLoad" VARCHAR, 
	"archivedAt" JSON, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "SendOutOrderResultsArchive" (
	id SERIAL NOT NULL, 
	"accessionId" VARCHAR, 
	"orderId" INTEGER, 
	"biomarkerId" INTEGER, 
	"testId" INTEGER, 
	result VARCHAR, 
	version INTEGER, 
	"biomarkerResultedAt" VARCHAR, 
	flag VARCHAR, 
	"addedBy" INTEGER, 
	"resultRemarks" VARCHAR, 
	"isResultAvailable" BOOLEAN, 
	"microbialLoad" VARCHAR, 
	"archivedAt" JSON, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "SendoutBatches" (
	id SERIAL NOT NULL, 
	"sendoutLabId" INTEGER, 
	"sampleCount" INTEGER, 
	"panelIds" JSON[], 
	"sampleIds" INTEGER[], 
	"createdBy" INTEGER, 
	"labName" VARCHAR, 
	"testIds" JSON[], 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_SendoutBatches_sendoutLabId" ON "SendoutBatches" ("sendoutLabId");

CREATE TABLE IF NOT EXISTS "SmsLogs" (
	id SERIAL NOT NULL, 
	"toNumber" VARCHAR, 
	purpose VARCHAR, 
	message TEXT, 
	error VARCHAR, 
	"isDelivered" BOOLEAN, 
	"providerResponse" JSON, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_SmsLogs_toNumber" ON "SmsLogs" ("toNumber");

CREATE TABLE IF NOT EXISTS "SmsSecurities" (
	id SERIAL NOT NULL, 
	code VARCHAR, 
	"mobileNumber" VARCHAR, 
	purpose VARCHAR, 
	"expiryTime" VARCHAR, 
	"isActive" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_SmsSecurities_mobileNumber" ON "SmsSecurities" ("mobileNumber");

CREATE TABLE IF NOT EXISTS "SmsTemplates" (
	id SERIAL NOT NULL, 
	purpose VARCHAR, 
	message TEXT, 
	variables JSON, 
	"isActive" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "Sops" (
	id SERIAL NOT NULL, 
	sop_name VARCHAR, 
	sop_number VARCHAR, 
	reviewer_name VARCHAR, 
	date_of_review TIMESTAMP WITH TIME ZONE, 
	created_by INTEGER, 
	"labId" INTEGER, 
	created_on TIMESTAMP WITH TIME ZONE, 
	updated_on TIMESTAMP WITH TIME ZONE, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "StateCityStaticData" (
	id SERIAL NOT NULL, 
	city VARCHAR, 
	state VARCHAR, 
	zipcode VARCHAR, 
	timezone VARCHAR, 
	"isActive" VARCHAR, 
	county VARCHAR, 
	country VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_StateCityStaticData_zipcode" ON "StateCityStaticData" (zipcode);

CREATE TABLE IF NOT EXISTS "StateReportingSessions" (
	id SERIAL NOT NULL, 
	"stateReportingId" INTEGER, 
	attempt INTEGER, 
	"reportingTime" VARCHAR, 
	status VARCHAR, 
	reason VARCHAR, 
	"responseData" JSON, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_StateReportingSessions_stateReportingId" ON "StateReportingSessions" ("stateReportingId");

CREATE TABLE IF NOT EXISTS "StateReportings" (
	id SERIAL NOT NULL, 
	"panelDetails" JSON, 
	"sampleIds" INTEGER[], 
	"reportingTime" VARCHAR, 
	status VARCHAR, 
	attachment JSON, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "SystemConfigs" (
	id SERIAL NOT NULL, 
	title VARCHAR, 
	"billingReportHeaders" JSON[], 
	"patientsReportHeaders" JSON[], 
	logo JSON, 
	"miniLogo" JSON, 
	url VARCHAR, 
	"labConfiguration" JSON, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "SystemDocuments" (
	id SERIAL NOT NULL, 
	title VARCHAR, 
	url VARCHAR, 
	description TEXT, 
	"isActive" BOOLEAN, 
	"createdBy" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "SystemLabDocument" (
	id SERIAL NOT NULL, 
	title VARCHAR, 
	url VARCHAR, 
	"createdBy" INTEGER, 
	"isActive" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "TestAttachments" (
	id SERIAL NOT NULL, 
	"testId" INTEGER, 
	"fileName" VARCHAR, 
	"mimeType" VARCHAR, 
	"fileSize" INTEGER, 
	path VARCHAR, 
	"secureUrl" VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "TestPanel" (
	id SERIAL NOT NULL, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "TestQuestion" (
	id SERIAL NOT NULL, 
	question VARCHAR, 
	options VARCHAR[], 
	answer VARCHAR, 
	"videoUrl" VARCHAR, 
	"answerDescription" VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "TestReportLayout" (
	id SERIAL NOT NULL, 
	title VARCHAR, 
	code VARCHAR, 
	url VARCHAR, 
	"isMultipleTable" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "Tests" (
	id SERIAL NOT NULL, 
	name VARCHAR, 
	code VARCHAR, 
	"sampleType" VARCHAR, 
	"sampleCollectionDeviceName" VARCHAR, 
	"sampleQuantity" VARCHAR, 
	description TEXT, 
	"createdBy" INTEGER, 
	"isIntakeFormRequired" BOOLEAN, 
	"formId" INTEGER, 
	"isStateReportingRequired" BOOLEAN, 
	"stateReporting" JSON, 
	"isBulkImportRequired" BOOLEAN, 
	"isActive" BOOLEAN, 
	"biomarkerIds" INTEGER[], 
	status VARCHAR, 
	"chatId" INTEGER, 
	"resultingMode" VARCHAR, 
	"kitComponents" VARCHAR[], 
	"kitImages" VARCHAR[], 
	questions INTEGER[], 
	"testLayoutDetails" JSON[], 
	"icdCodes" INTEGER[], 
	"isIcdCodeRequired" BOOLEAN, 
	"cptCodes" INTEGER[], 
	"isCptCodeRequired" BOOLEAN, 
	"cptCodeDetails" JSON[], 
	"testCategory" VARCHAR, 
	"departmentIds" INTEGER[], 
	"reagentIds" INTEGER[], 
	"instrumentIds" INTEGER[], 
	"reportFormat" VARCHAR, 
	"alertLimit" NUMERIC, 
	"maxLimit" NUMERIC, 
	"hasOrderingLimit" BOOLEAN, 
	"isLinkedTest" BOOLEAN, 
	"linkedTestId" NUMERIC, 
	"linkedTestText" VARCHAR, 
	"internalTestId" VARCHAR, 
	"integrationDetails" JSON, 
	"loincCode" VARCHAR, 
	"lastBarcodeCount" INTEGER, 
	"processOverView" VARCHAR, 
	"videoUrl" VARCHAR, 
	"kitRedirectUrl" VARCHAR, 
	"normalPdfTemplatePath" VARCHAR, 
	"abnormalPdfTemplatePath" VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "Tokens" (
	id SERIAL NOT NULL, 
	"userId" INTEGER, 
	token TEXT, 
	"expiryTime" VARCHAR, 
	"isActive" BOOLEAN, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_Tokens_userId" ON "Tokens" ("userId");

CREATE TABLE IF NOT EXISTS "UploadResultSessions" (
	id SERIAL NOT NULL, 
	"worklistId" INTEGER, 
	"worklistDetails" JSON, 
	"testId" INTEGER, 
	"biomarkerId" INTEGER, 
	"testCode" VARCHAR, 
	"biomarkerCode" VARCHAR, 
	"biomarkerDetails" JSON, 
	"accessionIds" JSON, 
	"sampleType" VARCHAR, 
	status VARCHAR, 
	"isManual" BOOLEAN, 
	"isDiscarded" BOOLEAN, 
	"fileName" VARCHAR, 
	"runMetadata" JSON, 
	"cqCutoff" FLOAT, 
	"createdBy" INTEGER, 
	"createdByDetails" JSON, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_UploadResultSessions_worklistId" ON "UploadResultSessions" ("worklistId");

CREATE TABLE IF NOT EXISTS "UserAclModels" (
	id SERIAL NOT NULL, 
	"userId" INTEGER, 
	"moduleAccess" VARCHAR, 
	"featureAccess" VARCHAR, 
	"apiAccess" VARCHAR[], 
	"roleId" INTEGER, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_UserAclModels_userId" ON "UserAclModels" ("userId");

CREATE TABLE IF NOT EXISTS "UserStaticData" (
	id SERIAL NOT NULL, 
	title VARCHAR, 
	value JSON[], 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_UserStaticData_title" ON "UserStaticData" (title);

CREATE TABLE IF NOT EXISTS "Users" (
	id SERIAL NOT NULL, 
	prefix VARCHAR, 
	suffix VARCHAR, 
	"firstName" VARCHAR, 
	"middleName" VARCHAR, 
	"lastName" VARCHAR, 
	"mobileNumber" VARCHAR, 
	"secondaryMobileNumber" VARCHAR, 
	"mobileNumberCode" VARCHAR, 
	"faxNumber" VARCHAR, 
	"addressLine1" VARCHAR, 
	"addressLine2" VARCHAR, 
	"dateOfBirth" VARCHAR, 
	zipcode VARCHAR, 
	state VARCHAR, 
	city VARCHAR, 
	"emailId" VARCHAR, 
	"npiNumber" VARCHAR, 
	"pTanNumber" VARCHAR, 
	"specialityType" VARCHAR, 
	"tinNumber" VARCHAR, 
	designation VARCHAR, 
	gender VARCHAR, 
	"roleId" INTEGER, 
	"roleObj" JSON, 
	password VARCHAR, 
	"isSdiUser" BOOLEAN, 
	"isPhysician" BOOLEAN, 
	"taxonomyDetails" JSON, 
	"isSameAddress" BOOLEAN, 
	"isActive" BOOLEAN, 
	"isEmailVerified" BOOLEAN, 
	"isDeleted" BOOLEAN, 
	"createdBy" INTEGER, 
	"isHybrid" BOOLEAN, 
	signature TEXT, 
	"signatureCount" INTEGER, 
	"internalUserId" VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS "ix_Users_emailId" ON "Users" ("emailId");

CREATE TABLE IF NOT EXISTS "Validations" (
	id SERIAL NOT NULL, 
	name_of_document VARCHAR, 
	test_id INTEGER, 
	biomarker_cutoff_value JSON, 
	created_by INTEGER, 
	"labId" INTEGER, 
	created_on TIMESTAMP WITH TIME ZONE, 
	updated_on TIMESTAMP WITH TIME ZONE, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "VersioningFile" (
	id SERIAL NOT NULL, 
	module VARCHAR, 
	"entityId" INTEGER, 
	"createdBy" INTEGER, 
	"labId" INTEGER, 
	"secureUrl" VARCHAR, 
	"mimeType" VARCHAR, 
	title VARCHAR, 
	"createdAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	"updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

