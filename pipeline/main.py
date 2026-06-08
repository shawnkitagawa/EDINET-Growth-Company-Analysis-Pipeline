from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo 
import gc

from scripts.fetch_edinet_data.download_document_csv import save_documents_to_csv
from scripts.fetch_edinet_data.fetch_document_metadata import run_edinet_metadata_pipeline
from core.storage import upload_folder_to_gcs



# Uncomment code are initial backfill 

def main():
    today_jst = datetime.now(ZoneInfo("Asia/Tokyo")).date()

    start_date = today_jst - timedelta(days=1)
    # start = datetime.strptime(start_date, "%Y-%m-%d").date()

    end_date = today_jst - timedelta(days=1)
    # date_length = (end_date - start).days + 1
    date_length = (end_date - start_date).days + 1 

    end_date_str = end_date.isoformat()
    # folder_name = f"{start_date}_to_{end_date_str}"
    folder_name = start_date.isoformat()

    print("STEP 1: Starting EDINET metadata pipeline", flush=True)
    result = run_edinet_metadata_pipeline(
        start_date=start_date.isoformat(),
        date_length=date_length,
        file_name= folder_name
    )
    print("STEP 1: Finished EDINET metadata pipeline", flush=True)

    if result is None: 
        print("No documents to download. Pipeline finished successfully.", flush=True)
        return

    print("STEP 2: Starting document CSV download/conversion and upload to GCS", flush=True)
    save_documents_to_csv(
        json_path=f"data/raw/metadata/json/edinet_documents_{folder_name}.json",
        start_date=start_date.isoformat(),
        end_date=end_date_str
    )
    print("STEP 2: Finished document CSV download/conversion and upload to GCS", flush=True)

    gc.collect()
    print("Memory cleanup completed before metadata upload", flush=True)

    print("STEP 3: Uploading metadata CSV folder to GCS", flush=True)
    upload_folder_to_gcs(
        local_folder="data/raw/metadata/csv",
        destination_prefix=f"raw/metadata/csv/{folder_name}"
    )
    print("STEP 3: Finished uploading metadata CSV folder", flush=True)

    # print("STEP 4: Uploading reference CSV folder to GCS", flush=True)
    # upload_folder_to_gcs(
    #     local_folder="data/raw/reference",
    #     destination_prefix="raw/reference/csv"
    # )
    # print("STEP 4: Finished uploading reference CSV folder", flush=True)

    print("PIPELINE FINISHED SUCCESSFULLY", flush=True)


if __name__ == "__main__":
    main()