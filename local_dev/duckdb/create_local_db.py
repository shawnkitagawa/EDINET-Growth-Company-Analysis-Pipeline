from pathlib import Path 
import duckdb

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT/'LOCAL_DEV'/ 'data'/'processed'/'edinet.duckdb'
SAMPLE_DATA = ROOT/'LOCAL_DEV'/'data'/'raw'

conn = duckdb.connect(str(DB_PATH))


# csv_path = SAMPLE_DATA/'metadata'/'csv'/'edinet_documents_2026-01-01_to_2026-05-19.csv'

# with open(csv_path, "rb") as f: 
#     raw = f.read(20)

# print(raw)

src = SAMPLE_DATA / "reference" / "EdinetcodeDlInfo.csv"
dst = SAMPLE_DATA / "reference" / "EdinetcodeDlInfo_utf8.csv"

# Original EDINET company master is Japanese Windows encoding.
text = src.read_text(encoding="cp932")

# Make a UTF-8 copy that DuckDB can read safely.
dst.write_text(text, encoding="utf-8-sig")




conn.execute(f"""

    CREATE OR REPLACE TABLE document_metadata_raw AS 
    SELECT * FROM read_csv_auto('{SAMPLE_DATA/'metadata'/'csv'/'edinet_documents_2026-01-01_to_2026-05-19.csv'}')
             """)

print("Metadata loaded")

company_master_csv = SAMPLE_DATA / 'reference' / 'EdinetcodeDlInfo.csv'

print("2. Loading company master...")

conn.execute(f"""
    CREATE OR REPLACE TABLE edinet_company_master_raw AS
    SELECT *
    FROM read_csv(
        '{dst.as_posix()}',
        delim = ',',
        header = true,
        all_varchar = true
    );
""")
print("Company master loaded")


annual_reports_glob = SAMPLE_DATA / 'documents' / '2026-01-01_to_2026-05-19' / '*.csv'

conn.execute(f"""
    CREATE OR REPLACE TABLE raw_annual_reports AS 
    SELECT *
    FROM read_csv(
        '{annual_reports_glob.as_posix()}',
        encoding = 'utf-16',
        delim = '\t',
        header = true,
        all_varchar = true,
        union_by_name = true,
        strict_mode = false
    );
""")

conn.execute("""
    CREATE OR REPLACE TABLE stg_annual_report_values_cleaned AS
    SELECT DISTINCT
        docID,
        element_id,
        item_name,
        context_id,
        relative_year,
        consolidated_type,
        period_type,
        unit_name,
        value_text
    FROM raw_annual_report_values
""")

for table in ['document_metadata_raw', 'edinet_company_master_raw', 'raw_annual_report_values']:
 count = conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
 print(f"{table}:{count} rows")
print("Annual reports loaded")
conn.close()


