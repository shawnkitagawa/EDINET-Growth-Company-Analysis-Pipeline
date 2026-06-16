from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo 
import gc

from scripts.fetch_edinet_data.download_document_csv import download_document_csvs_to_gcs
from scripts.fetch_edinet_data.fetch_document_metadata import run_edinet_metadata_pipeline


def main():
    today_jst = datetime.now(ZoneInfo("Asia/Tokyo")).date()
    start_date = today_jst - timedelta(days=1)
    end_date = today_jst - timedelta(days=1)
    date_length = (end_date - start_date).days + 1 
    folder_name = start_date.isoformat()

    print("STEP 1: Starting EDINET metadata pipeline and upload to GCS", flush=True)
    result = run_edinet_metadata_pipeline(
        start_date=start_date.isoformat(),
        date_length=date_length,
        file_name= folder_name
    )
    print("STEP 1: Finished EDINET metadata pipeline", flush=True)

    print("STEP 2: Starting document CSV download/conversion and upload to GCS", flush=True)
    download_document_csvs_to_gcs(
        start_date=start_date.isoformat(),
        document_informations= result
    )
    print("STEP 2: Finished document CSV download/conversion and upload to GCS", flush=True)

    print("PIPELINE FINISHED SUCCESSFULLY", flush=True)


if __name__ == "__main__":
    main()