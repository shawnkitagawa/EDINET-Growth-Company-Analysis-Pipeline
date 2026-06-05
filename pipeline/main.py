from datetime import date, datetime
from scripts.fetch_edinet_data.download_document_csv import save_documents_to_csv
from scripts.fetch_edinet_data.fetch_document_metadata import run_edinet_metadata_pipeline
from core.storage import upload_folder_to_gcs


def main():
    start_date = "2026-01-01"
    start = datetime.strptime(start_date, "%Y-%m-%d").date()

    end_date = date.today()
    date_length = (end_date - start).days + 1

    end_date_str = end_date.isoformat()
    folder_name = f"{start_date}_to_{end_date_str}"

    bucket_name = "edinet-growth-pipeline-data"

    run_edinet_metadata_pipeline(
        start_date=start_date,
        date_length=date_length
    )

    save_documents_to_csv(
        json_path=f"data/raw/metadata/json/edinet_documents_{folder_name}.json",
        start_date=start_date,
        end_date=end_date_str
    )

    # Metadata CSV
    upload_folder_to_gcs(
        local_folder="data/raw/metadata/csv",
        bucket_name=bucket_name,
        destination_prefix=f"raw/metadata/csv/{folder_name}"
    )

    # Documents CSV
    upload_folder_to_gcs(
        local_folder=f"data/raw/documents/{folder_name}",
        bucket_name=bucket_name,
        destination_prefix=f"raw/documents/{folder_name}"
    )

    # Reference CSV
    upload_folder_to_gcs(
        local_folder="data/raw/reference",
        bucket_name=bucket_name,
        destination_prefix="raw/reference/csv"
    )


if __name__ == "__main__":
    main()