from scripts.step2_duckdb_analysis.database import connect_db
from scripts.step2_duckdb_analysis.file_utils import print_table_counts, read_japanese_table
from core.config import ANNUAL_REPORT_CSV_DIR
import pandas as pd 


def create_raw_annual_report_values_pipeline(folder_name: str):

    con = connect_db()

    target_dir = ANNUAL_REPORT_CSV_DIR / folder_name
    csv_files = sorted(target_dir.glob("*.csv"))

    print(f"\nLooking for annual report CSV files in: {target_dir.resolve()}")

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {target_dir}")

    print(f"Found {len(csv_files)} annual report CSV files.")

    failed_files = []
    loaded_files = 0

    create_raw_annual_report_values_tables(con=con)

    for csv_path in csv_files:
        doc_id = csv_path.stem
        print(f"Loading {doc_id}")

        try:
            loaded_files = insert_raw_annual_report(
                con=con,
                csv_path=csv_path,
                loaded_files=loaded_files,
                doc_id=doc_id
            )

        except Exception as e:
            print(f"Failed to load {csv_path}: {e}")
            failed_files.append(str(csv_path))

    print("\n=== CSV loading summary ===")
    print(f"Total files: {len(csv_files)}")
    print(f"Loaded files: {loaded_files}")
    print(f"Failed files: {len(failed_files)}")

    if failed_files:
        print("\nFailed file examples:")
        for file in failed_files[:10]:
            print(file)

    con.close()



def create_raw_annual_report_values_tables(con): 
    con.execute("DROP TABLE IF EXISTS raw_annual_report_values")

    con.execute("""
        CREATE TABLE raw_annual_report_values (
            docID VARCHAR,
            element_id VARCHAR,
            item_name VARCHAR,
            context_id VARCHAR,
            relative_year VARCHAR,
            consolidated_type VARCHAR,
            period_type VARCHAR,
            unit_id VARCHAR,
            unit_name VARCHAR,
            value_text VARCHAR
        );
    """)



def insert_raw_annual_report(con, csv_path, loaded_files, doc_id): 
    df = read_japanese_table(csv_path, sep="\t")

    required_columns = [
        "要素ID",
        "項目名",
        "コンテキストID",
        "相対年度",
        "連結・個別",
        "期間・時点",
        "ユニットID",
        "単位",
        "値",
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    clean_df = pd.DataFrame({
        "docID": doc_id,
        "element_id": df["要素ID"],
        "item_name": df["項目名"],
        "context_id": df["コンテキストID"],
        "relative_year": df["相対年度"],
        "consolidated_type": df["連結・個別"],
        "period_type": df["期間・時点"],
        "unit_id": df["ユニットID"],
        "unit_name": df["単位"],
        "value_text": df["値"],
    })

    con.register("temp_annual_report_df", clean_df)

    con.execute("""
        INSERT INTO raw_annual_report_values
        SELECT *
        FROM temp_annual_report_df;
    """)

    con.unregister("temp_annual_report_df")

    loaded_files += 1
    return loaded_files



# Deprecated: replaced by dbt model
def create_annual_report_revenue_tables(con): 
    con.execute("""
        CREATE OR REPLACE TABLE annual_report_revenue AS
        SELECT
            docID,

            MAX(CASE
                WHEN element_id = 'jpcrp_cor:NetSalesSummaryOfBusinessResults'
                 AND context_id = 'Prior5YearDuration'
                THEN TRY_CAST(value_text AS BIGINT)
            END) AS sales_5_years_ago,

            MAX(CASE
                WHEN element_id = 'jpcrp_cor:NetSalesSummaryOfBusinessResults'
                 AND context_id = 'Prior4YearDuration'
                THEN TRY_CAST(value_text AS BIGINT)
            END) AS sales_4_years_ago,

            MAX(CASE
                WHEN element_id = 'jpcrp_cor:NetSalesSummaryOfBusinessResults'
                 AND context_id = 'Prior3YearDuration'
                THEN TRY_CAST(value_text AS BIGINT)
            END) AS sales_3_years_ago,

            MAX(CASE
                WHEN element_id = 'jpcrp_cor:NetSalesSummaryOfBusinessResults'
                 AND context_id = 'Prior2YearDuration'
                THEN TRY_CAST(value_text AS BIGINT)
            END) AS sales_2_years_ago,

            MAX(CASE
                WHEN element_id = 'jpcrp_cor:NetSalesSummaryOfBusinessResults'
                 AND context_id = 'Prior1YearDuration'
                THEN TRY_CAST(value_text AS BIGINT)
            END) AS previous_sales,

            MAX(CASE
                WHEN element_id = 'jpcrp_cor:NetSalesSummaryOfBusinessResults'
                 AND context_id = 'CurrentYearDuration'
                THEN TRY_CAST(value_text AS BIGINT)
            END) AS current_sales

        FROM raw_annual_report_values
        GROUP BY docID;
    """)

    # Depreceated: replace by dbt model 
def create_company_growth_analysis_tables(con):
    con.execute("""
        CREATE OR REPLACE TABLE company_growth_analysis AS
        SELECT
            f.edinetCode,
            f.filerName,
            f.docID,
            f.periodStart,
            f.periodEnd,

            r.sales_5_years_ago,
            r.sales_4_years_ago,
            r.sales_3_years_ago,
            r.sales_2_years_ago,
            r.previous_sales,
            r.current_sales,

            CASE
                WHEN r.current_sales IS NULL THEN NULL
                WHEN r.previous_sales IS NULL THEN NULL
                WHEN r.previous_sales = 0 THEN NULL
                ELSE (r.current_sales - r.previous_sales) * 1.0 / r.previous_sales
            END AS one_year_growth_rate,

            CASE
                WHEN r.current_sales IS NULL THEN NULL
                WHEN r.sales_4_years_ago IS NULL THEN NULL
                WHEN r.sales_4_years_ago = 0 THEN NULL
                ELSE (r.current_sales - r.sales_4_years_ago) * 1.0 / r.sales_4_years_ago
            END AS four_year_total_growth_rate,

            CASE
                WHEN r.current_sales IS NULL THEN NULL
                WHEN r.sales_4_years_ago IS NULL THEN NULL
                WHEN r.sales_4_years_ago <= 0 THEN NULL
                WHEN r.current_sales <= 0 THEN NULL
                ELSE POWER(r.current_sales * 1.0 / r.sales_4_years_ago, 1.0 / 4) - 1
            END AS four_year_cagr,

            CASE
                WHEN r.current_sales IS NULL THEN NULL
                WHEN r.sales_5_years_ago IS NULL THEN NULL
                WHEN r.sales_5_years_ago = 0 THEN NULL
                ELSE (r.current_sales - r.sales_5_years_ago) * 1.0 / r.sales_5_years_ago
            END AS five_year_growth_rate,

            CASE
                WHEN r.sales_2_years_ago IS NOT NULL
                 AND r.previous_sales IS NOT NULL
                 AND r.current_sales IS NOT NULL
                 AND r.sales_2_years_ago > 0
                 AND r.previous_sales > r.sales_2_years_ago
                 AND r.current_sales > r.previous_sales
                THEN TRUE
                ELSE FALSE
            END AS two_year_consecutive_growth,
                

            CASE
                WHEN r.sales_4_years_ago IS NOT NULL
                 AND r.sales_3_years_ago IS NOT NULL
                 AND r.sales_2_years_ago IS NOT NULL
                 AND r.previous_sales IS NOT NULL
                 AND r.current_sales IS NOT NULL
                 AND r.sales_4_years_ago > 0
                 AND r.sales_3_years_ago > r.sales_4_years_ago
                 AND r.sales_2_years_ago > r.sales_3_years_ago
                 AND r.previous_sales > r.sales_2_years_ago
                 AND r.current_sales > r.previous_sales
                THEN TRUE
                ELSE FALSE
            END AS four_year_consecutive_growth

        FROM finalized_annual_report_metadata f
        LEFT JOIN annual_report_revenue r
            ON f.docID = r.docID;
    """)


# Depreceated: replace by dbt model
def table_check(con): 

    print_table_counts(con, [
        "raw_annual_report_values",
        "annual_report_revenue",
        "company_growth_analysis",
    ])

    print("\n=== Sales extraction check ===")
    print(con.execute("""
        SELECT
            COUNT(*) AS total_companies,
            COUNT(current_sales) AS companies_with_current_sales,
            COUNT(previous_sales) AS companies_with_previous_sales,
            COUNT(sales_4_years_ago) AS companies_with_sales_4_years_ago,
            COUNT(one_year_growth_rate) AS companies_with_one_year_growth_rate,
            COUNT(four_year_total_growth_rate) AS companies_with_four_year_total_growth_rate,
            COUNT(four_year_cagr) AS companies_with_four_year_cagr
        FROM company_growth_analysis;
    """).fetchdf())

    print("\n=== Sample extracted revenue ===")
    print(con.execute("""
        SELECT *
        FROM annual_report_revenue
        LIMIT 10;
    """).fetchdf())



