from pathlib import Path
from scripts.step2_duckdb_analysis.database import connect_db

# Depreceated: replace by dbt model
def create_high_growth_pipeline():

    con = connect_db()

    create_high_growth_tables(con)

    # Main final output table
    con.execute("""
        CREATE OR REPLACE TABLE high_growth_companies AS
        SELECT *
        FROM high_growth_four_year_cagr;
    """)
    print("\nCreated high-growth comparison tables.")
    
    print_analysis_result(con, 20)

    output_analysis_result(con = con)
    Path("outputs").mkdir(parents=True, exist_ok=True)

    con.close()


# Depreceated: replace by dbt model
def create_high_growth_tables(con): 
  
    con.execute("""
        CREATE OR REPLACE TABLE high_growth_one_year AS
        SELECT *
        FROM company_growth_analysis_with_industry
        WHERE one_year_growth_rate IS NOT NULL
          AND one_year_growth_rate >= 0.40
        ORDER BY one_year_growth_rate DESC;
    """)

    con.execute("""
        CREATE OR REPLACE TABLE high_growth_four_year_total AS
        SELECT *
        FROM company_growth_analysis_with_industry
        WHERE four_year_total_growth_rate IS NOT NULL
          AND four_year_total_growth_rate >= 0.40
          AND sales_4_years_ago >= 100000000
        ORDER BY four_year_total_growth_rate DESC;
    """)

    con.execute("""
        CREATE OR REPLACE TABLE high_growth_four_year_cagr AS
        SELECT *
        FROM company_growth_analysis_with_industry
        WHERE four_year_cagr IS NOT NULL
          AND four_year_cagr >= 0.40
          AND sales_4_years_ago >= 100000000
        ORDER BY four_year_cagr DESC;
    """)

    
    con.execute("""
        CREATE OR REPLACE TABLE strict_high_growth_companies AS
        SELECT *
        FROM company_growth_analysis_with_industry
        WHERE four_year_cagr IS NOT NULL
          AND four_year_cagr >= 0.40
          AND sales_4_years_ago >= 100000000
          AND four_year_consecutive_growth = TRUE
        ORDER BY four_year_cagr DESC;
    """)


# Depreceated: replace by dbt model
def print_analysis_result(con, limit: int): 
    print("\n=== High-growth table counts ===")
    print(con.execute("""
        SELECT 'one_year_growth >= 40%' AS metric, COUNT(*) AS company_count
        FROM high_growth_one_year

        UNION ALL

        SELECT 'four_year_total_growth >= 40%' AS metric, COUNT(*) AS company_count
        FROM high_growth_four_year_total

        UNION ALL

        SELECT 'four_year_cagr >= 40%' AS metric, COUNT(*) AS company_count
        FROM high_growth_four_year_cagr

        UNION ALL

        SELECT 'strict four_year_cagr >= 40%' AS metric, COUNT(*) AS company_count
        FROM strict_high_growth_companies;
    """).fetchdf())

    print("\n=== Top high-growth companies by one-year growth ===")
    print(con.execute(f"""
        SELECT
            edinetCode,
            filerName,
            industry,
            docID,
            periodEnd,
            previous_sales,
            current_sales,
            one_year_growth_rate
        FROM high_growth_one_year
        ORDER BY one_year_growth_rate DESC
        LIMIT {limit};
    """).fetchdf())

    print("\n=== Top high-growth companies by four-year total growth ===")
    print(con.execute(f"""
        SELECT
            edinetCode,
            filerName,
            industry,
            docID,
            periodEnd,
            sales_4_years_ago,
            current_sales,
            four_year_total_growth_rate
        FROM high_growth_four_year_total
        ORDER BY four_year_total_growth_rate DESC
        LIMIT {limit};
    """).fetchdf())

    print("\n=== Top high-growth companies by four-year CAGR ===")
    print(con.execute(f"""
        SELECT
            edinetCode,
            filerName,
            industry,
            docID,
            periodEnd,
            sales_4_years_ago,
            current_sales,
            four_year_total_growth_rate,
            four_year_cagr,
            four_year_consecutive_growth
        FROM high_growth_companies
        ORDER BY four_year_consecutive_growth
        LIMIT {limit};
    """).fetchdf())

    print("\n=== Strict high-growth companies by four-year CAGR ===")
    print(con.execute(f"""
        SELECT
            edinetCode,
            filerName,
            industry,
            docID,
            periodEnd,
            sales_4_years_ago,
            current_sales,
            four_year_total_growth_rate,
            four_year_cagr,
            four_year_consecutive_growth
        FROM strict_high_growth_companies
        ORDER BY four_year_consecutive_growth
        LIMIT {limit};
    """).fetchdf())


# Depreceated: replace by dbt model    
def output_analysis_result(con): 
    con.execute("""
        COPY high_growth_one_year
        TO 'outputs/high_growth_one_year.csv'
        WITH (HEADER, DELIMITER ',');
    """)

    con.execute("""
        COPY high_growth_four_year_total
        TO 'outputs/high_growth_four_year_total.csv'
        WITH (HEADER, DELIMITER ',');
    """)

    con.execute("""
        COPY high_growth_four_year_cagr
        TO 'outputs/high_growth_four_year_cagr.csv'
        WITH (HEADER, DELIMITER ',');
    """)

    con.execute("""
        COPY strict_high_growth_companies
        TO 'outputs/strict_high_growth_companies.csv'
        WITH (HEADER, DELIMITER ',');
    """)

    con.execute("""
        COPY high_growth_companies
        TO 'outputs/high_growth_companies.csv'
        WITH (HEADER, DELIMITER ',');
    """)

    print("\nExported output CSV files.")
