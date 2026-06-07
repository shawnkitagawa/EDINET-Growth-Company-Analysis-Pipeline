USE ROLE ACCOUNTADMIN;
USE DATABASE EDINET_DB;
USE SCHEMA RAW;

-- ============================================================
-- Pipe 1: Document metadata
-- GCS path example:
-- raw/metadata/csv/2026-01-01_to_2026-06-06/metadata.csv
-- ============================================================

CREATE OR REPLACE PIPE DOCUMENT_METADATA_PIPE
  AUTO_INGEST = TRUE
  INTEGRATION = GCS_EDINET_NOTIFICATION_INT
AS
COPY INTO DOCUMENT_METADATA_RAW (
    docID,
    edinetCode,
    filerName,
    docDescription,
    periodStart,
    periodEnd,
    submitDateTime,
    formCode,
    docTypeCode,
    fetchDate,
    raw_file_name,
    loaded_at
)
FROM (
    SELECT
        $1::STRING,
        $2::STRING,
        $3::STRING,
        $4::STRING,
        TRY_TO_DATE($5),
        TRY_TO_DATE($6),
        TRY_TO_TIMESTAMP_NTZ($7),
        $8::STRING,
        $9::STRING,
        TRY_TO_DATE($10),
        METADATA$FILENAME,
        CURRENT_TIMESTAMP()
    FROM @EDINET_METADATA_STAGE
)
FILE_FORMAT = (FORMAT_NAME = EDINET_CSV_FORMAT);


-- ============================================================
-- Pipe 2: EDINET company master
-- GCS path example:
-- raw/company_master/csv/company_master.csv
-- ============================================================

CREATE OR REPLACE PIPE EDINET_COMPANY_MASTER_PIPE
  AUTO_INGEST = TRUE
  INTEGRATION = GCS_EDINET_NOTIFICATION_INT
AS
COPY INTO EDINET_COMPANY_MASTER_RAW (
    edinetCode,
    master_filerName,
    industry,
    secCode,
    fiscal_year_end,
    listing_status,
    has_consolidated,
    raw_file_name,
    loaded_at
)
FROM (
    SELECT
        $1::STRING,
        $2::STRING,
        $3::STRING,
        $4::STRING,
        $5::STRING,
        $6::STRING,
        $7::STRING,
        METADATA$FILENAME,
        CURRENT_TIMESTAMP()
    FROM @EDINET_COMPANY_MASTER_STAGE
)
FILE_FORMAT = (FORMAT_NAME = EDINET_CSV_FORMAT);


-- ============================================================
-- Pipe 3: Raw annual report values
-- GCS path example:
-- raw/documents/2026-01-01_to_2026-06-06/S100XXXX.csv
-- ============================================================

CREATE OR REPLACE PIPE RAW_ANNUAL_REPORT_VALUES_PIPE
  AUTO_INGEST = TRUE
  INTEGRATION = GCS_EDINET_NOTIFICATION_INT
AS
COPY INTO RAW_ANNUAL_REPORT_VALUES (
    docID,
    element_id,
    item_name,
    context_id,
    relative_year,
    consolidated_type,
    period_type,
    unit_id,
    unit_name,
    value_text,
    raw_file_name,
    loaded_at
)
FROM (
    SELECT
        $1::STRING,
        $2::STRING,
        $3::STRING,
        $4::STRING,
        $5::STRING,
        $6::STRING,
        $7::STRING,
        $8::STRING,
        $9::STRING,
        $10::STRING,
        METADATA$FILENAME,
        CURRENT_TIMESTAMP()
    FROM @EDINET_ANNUAL_REPORT_VALUES_STAGE
)
FILE_FORMAT = (FORMAT_NAME = EDINET_CSV_FORMAT);