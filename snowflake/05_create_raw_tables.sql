USE ROLE ACCOUNTADMIN;
USE DATABASE EDINET_DB;
USE SCHEMA RAW;

CREATE OR REPLACE TABLE DOCUMENT_METADATA_RAW (
    docID STRING,
    edinetCode STRING,
    filerName STRING,
    docDescription STRING,
    periodStart DATE,
    periodEnd DATE,
    submitDateTime TIMESTAMP_NTZ,
    formCode STRING,
    docTypeCode STRING,
    fetchDate DATE,

    raw_file_name STRING,
    loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE TABLE EDINET_COMPANY_MASTER_RAW (
    edinetCode STRING,
    master_filerName STRING,
    industry STRING,
    secCode STRING,
    fiscal_year_end STRING,
    listing_status STRING,
    has_consolidated STRING,

    raw_file_name STRING,
    loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE TABLE RAW_ANNUAL_REPORT_VALUES (
    docID STRING,
    element_id STRING,
    item_name STRING,
    context_id STRING,
    relative_year STRING,
    consolidated_type STRING,
    period_type STRING,
    unit_id STRING,
    unit_name STRING,
    value_text STRING,
    raw_file_name STRING,
    loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
