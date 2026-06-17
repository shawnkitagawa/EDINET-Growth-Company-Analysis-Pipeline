import duckdb

from core.config import DB_PATH, OUTPUT_DIR


def export_dbt_outputs():
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tables = [
        "high_growth_companies",
        "high_growth_four_year_cagr",
        "high_growth_four_year_total",
        "high_growth_one_year",
        "strict_high_growth_companies",
        "company_growth_analysis_with_industry",
    ]

    con = duckdb.connect(str(DB_PATH))

    for table_name in tables:
        output_path = OUTPUT_DIR / f"{table_name}.csv"

        con.execute(f"""
            COPY {table_name}
            TO '{output_path.as_posix()}'
            WITH (HEADER, DELIMITER ',');
        """)

        print(f"Exported: {output_path}")

    con.close()


if __name__ == "__main__":
    export_dbt_outputs()