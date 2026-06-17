
from scripts.step2_duckdb_analysis.database import connect_db
from scripts.step2_duckdb_analysis.file_utils import print_table_counts, check_duplicates
from core.config import METADATA_CSV_PATH

def create_document_tables(folder_name: str):

    con = connect_db()

    create_raw_document_tables(con, folder_name)

    print("Created raw document metadata table.")

    print_table_counts(con, [
        "document_metadata",
    ])

    con.close()


def create_raw_document_tables(con, folder_name): 

    con.execute(f"""
        CREATE OR REPLACE TABLE document_metadata AS
        SELECT
            docID,
            edinetCode,
            filerName,
            docDescription,
            TRY_CAST(periodStart AS DATE) AS periodStart,
            TRY_CAST(periodEnd AS DATE) AS periodEnd,
            TRY_CAST(submitDateTime AS TIMESTAMP) AS submitDateTime,
            formCode,
            CAST(docTypeCode AS VARCHAR) AS docTypeCode,
            TRY_CAST(fetchDate AS DATE) AS fetchDate
        FROM read_csv_auto('{f"{METADATA_CSV_PATH}/edinet_documents_{folder_name}.csv"}', header=True);
    """)


# Depreceated: replace by dbt model
def clean_annual_report_by_dates_tables(con): 
    con.execute(r"""
        CREATE OR REPLACE TABLE annual_reports_cleaned AS
        SELECT
            docID,
            edinetCode,
            filerName,
            docDescription,

            COALESCE(
                periodStart,
                TRY_CAST(
                    REPLACE(
                        regexp_extract(docDescription, '\((\d{4}/\d{2}/\d{2})－', 1),
                        '/',
                        '-'
                    ) AS DATE
                )
            ) AS periodStart,

            COALESCE(
                periodEnd,
                TRY_CAST(
                    REPLACE(
                        regexp_extract(docDescription, '－(\d{4}/\d{2}/\d{2})\)', 1),
                        '/',
                        '-'
                    ) AS DATE
                )
            ) AS periodEnd,

            submitDateTime,
            formCode,
            docTypeCode,
            fetchDate
        FROM document_metadata
        WHERE docTypeCode IN ('120', '130')
          AND formCode IN ('030000', '030001');
    """)


# Depreceated: replace by dbt model
def clean_latest_annual_report_by_doctype_versions(con): 
    con.execute("""
        CREATE OR REPLACE TABLE annual_reports_latest_version AS
        SELECT * EXCLUDE(row_num)
        FROM (
            SELECT
                *,
                ROW_NUMBER() OVER (
                    PARTITION BY edinetCode, periodStart, periodEnd
                    ORDER BY submitDateTime DESC
                ) AS row_num
            FROM annual_reports_cleaned
        )
        WHERE row_num = 1;
    """)


# Depreceated: replace by dbt model
def company_latest_report_tables(con): 

    con.execute("""
        CREATE OR REPLACE TABLE company_latest_annual_report AS
        SELECT * EXCLUDE(row_num)
        FROM (
            SELECT
                *,
                ROW_NUMBER() OVER (
                    PARTITION BY edinetCode
                    ORDER BY periodEnd DESC, submitDateTime DESC
                ) AS row_num
            FROM annual_reports_latest_version
        )
        WHERE row_num = 1;
    """)


# Depreceated: replace by dbt model
def finalize_metadata_tables(con): 
    con.execute("""
        CREATE OR REPLACE TABLE finalized_annual_report_metadata AS
        SELECT
            docID,
            edinetCode,
            filerName,
            docDescription,
            periodStart,
            periodEnd,
            submitDateTime,
            formCode,
            docTypeCode,
            fetchDate
        FROM company_latest_annual_report;
    """)
