import pandas as pd 
from pathlib import Path
from datetime import date, datetime

from scripts.step1_fetch_edinet_data.fetch_document_metadata import fetch_all_edinet_documents
from scripts.step1_fetch_edinet_data.download_document_csv import save_documents_to_csv

from scripts.step2_duckdb_analysis.create_document_tables import create_document_tables
from scripts.step2_duckdb_analysis.create_growth_tables import create_raw_annual_report_values_pipeline
from scripts.step2_duckdb_analysis.create_company_master_tables import create_company_master_pipeline


from datetime import date, datetime

from scripts.step1_fetch_edinet_data.fetch_document_metadata import run_edinet_metadata_pipeline
from scripts.step1_fetch_edinet_data.download_document_csv import save_documents_to_csv

from scripts.step2_duckdb_analysis.create_document_tables import create_document_tables
from scripts.step2_duckdb_analysis.create_growth_tables import create_raw_annual_report_values_pipeline
from scripts.step2_duckdb_analysis.create_company_master_tables import create_company_master_pipeline


def main():
    start_date = "2026-01-01"
    start = datetime.strptime(start_date, "%Y-%m-%d").date()

    end_date = date.today()
    date_length = (end_date - start).days + 1

    end_date_str = end_date.isoformat()
    folder_name = f"{start_date}_to_{end_date_str}"

    run_edinet_metadata_pipeline(
        start_date=start_date,
        date_length=date_length
    )

    save_documents_to_csv(
        json_path=f"data/raw/metadata/json/edinet_documents_{folder_name}.json",
        start_date=start_date,
        end_date=end_date_str
    )

    create_document_tables(folder_name = folder_name)

    create_raw_annual_report_values_pipeline(folder_name=folder_name)

    create_company_master_pipeline()


if __name__ == "__main__":
    main()