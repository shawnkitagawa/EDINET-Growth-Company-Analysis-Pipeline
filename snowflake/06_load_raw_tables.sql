USE ROLE ACCOUNTADMIN;
USE DATABASE EDINET_DB;
USE SCHEMA RAW;

TRUNCATE TABLE DOCUMENT_METADATA_RAW;
TRUNCATE TABLE EDINET_COMPANY_MASTER_RAW;
TRUNCATE TABLE RAW_ANNUAL_REPORT_VALUES;


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
FILE_FORMAT = (FORMAT_NAME = 'EDINET_CSV_FORMAT')
FORCE = TRUE;


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
    FROM @EDINET_REFERENCE_STAGE
)
FILE_FORMAT = (FORMAT_NAME = 'EDINET_SHIFTJIS_CSV_FORMAT')
FORCE = TRUE;


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
        REGEXP_REPLACE(
            REGEXP_SUBSTR(METADATA$FILENAME, '[^/]+$'),
            '\\.csv$',
            ''
        ) AS docID,
        $1::STRING AS element_id,
        $2::STRING AS item_name,
        $3::STRING AS context_id,
        $4::STRING AS relative_year,
        $5::STRING AS consolidated_type,
        $6::STRING AS period_type,
        $7::STRING AS unit_id,
        $8::STRING AS unit_name,
        $9::STRING AS value_text,
        METADATA$FILENAME AS raw_file_name,
        CURRENT_TIMESTAMP() AS loaded_at
    FROM @EDINET_DOCUMENTS_STAGE
)
FILE_FORMAT = (FORMAT_NAME = 'EDINET_TSV_UTF16_FORMAT')
FORCE = TRUE;