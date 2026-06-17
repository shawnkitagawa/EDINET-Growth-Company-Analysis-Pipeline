from scripts.step2_duckdb_analysis.database import connect_db
from pathlib import Path
from core.config import EDINET_CODE_LIST_PATH
import pandas as pd 
from scripts.step2_duckdb_analysis.file_utils import read_japanese_table, print_table_counts

def create_company_master_pipeline():

    con = connect_db()

    create_company_master_tables(con)

    print_table_counts(con, [
        "edinet_company_master"
    ])

    con.close()



def create_company_master_tables(con):
    company_master_path = Path(EDINET_CODE_LIST_PATH)

    if not company_master_path.exists():
        raise FileNotFoundError(
            f"Company master file not found: {company_master_path.resolve()}"
        )
    
    master_df = read_japanese_table(
        company_master_path,
        skiprows=1,
        sep=","
    )

    master_df.columns = (
        master_df.columns
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
    )

    print("\n=== Company master columns ===")
    print(master_df.columns.tolist())

    required_columns = [
        "ＥＤＩＮＥＴコード",
        "提出者名",
        "提出者業種",
        "証券コード",
        "決算日",
        "上場区分",
        "連結の有無",
    ]

    missing_columns = [col for col in required_columns if col not in master_df.columns]

    if missing_columns:
        raise ValueError(f"Company master missing columns: {missing_columns}")

    clean_master_df = pd.DataFrame({
        "edinetCode": master_df["ＥＤＩＮＥＴコード"],
        "master_filerName": master_df["提出者名"],
        "industry": master_df["提出者業種"],
        "secCode": master_df["証券コード"],
        "fiscal_year_end": master_df["決算日"],
        "listing_status": master_df["上場区分"],
        "has_consolidated": master_df["連結の有無"],
    })

    con.register("temp_company_master_df", clean_master_df)

    con.execute("""
        CREATE OR REPLACE TABLE edinet_company_master AS
        SELECT *
        FROM temp_company_master_df;
    """)

    con.unregister("temp_company_master_df")



# Depreceated: replace by dbt model
def company_growth_analysis_with_industry(con): 
    con.execute("""
        CREATE OR REPLACE TABLE company_growth_analysis_with_industry AS
        SELECT
            g.edinetCode,
            g.filerName,
            m.industry,
            m.secCode,
            m.fiscal_year_end,
            m.listing_status,
            m.has_consolidated,

            g.docID,
            g.periodStart,
            g.periodEnd,

            g.sales_5_years_ago,
            g.sales_4_years_ago,
            g.sales_3_years_ago,
            g.sales_2_years_ago,
            g.previous_sales,
            g.current_sales,

            g.one_year_growth_rate,
            g.four_year_total_growth_rate,
            g.four_year_cagr,
            g.five_year_growth_rate,
            g.two_year_consecutive_growth,
            g.four_year_consecutive_growth

        FROM company_growth_analysis g
        LEFT JOIN edinet_company_master m
            ON g.edinetCode = m.edinetCode;
    """)

    print("\nCreated company master and industry table.")