import json
import random
import time
import zipfile
from io import BytesIO
from google.cloud import storage

import requests

from pipeline.core.config import API_KEY, URL_DOWNLOAD, BUCKET_NAME


client= storage.Client()
bucket = client.bucket(BUCKET_NAME)



def download_document_csvs_to_gcs(
    document_informations: list[dict],
    start_date: str,
):
    if not document_informations:
        print("No documents to download. Exiting successfully.", flush=True)
        return []

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    params = {
        "type": 5,
        "Subscription-Key": API_KEY,
    }

    headers = {
        "User-Agent": "edinet-growth-pipeline/1.0",
        "Connection": "close",
    }

    failed_doc_ids = []
    consecutive_failures = 0
    max_consecutive_failures = 10

    for document in document_informations:
        doc_id = document["docID"]
        destination_path = f"raw/documents/{start_date}/{doc_id}.csv"

        blob = bucket.blob(destination_path)

        if blob.exists():
            print(f"Already exists, skipping: {destination_path}", flush=True)
            continue

        success = False

        for attempt in range(1, 4):
            try:
                url = f"{URL_DOWNLOAD}/{doc_id}"

                response = requests.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=(10, 20),
                )
                response.raise_for_status()

                with zipfile.ZipFile(BytesIO(response.content)) as z:
                    csv_files = [
                        name for name in z.namelist()
                        if name.lower().endswith(".csv")
                    ]

                    asr_files = [
                        name for name in csv_files
                        if "asr" in name.lower()
                    ]

                    if not asr_files:
                        print(f"No ASR CSV found for {doc_id}", flush=True)
                        success = True
                        break

                    selected_csv = asr_files[0]

                    with z.open(selected_csv) as source:
                        blob.upload_from_file(
                            source,
                            content_type="text/csv",
                            timeout=120,
                        )

                print(f"Uploaded directly to GCS: {destination_path}", flush=True)

                success = True
                consecutive_failures = 0
                break

            except (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.SSLError,
                requests.exceptions.ChunkedEncodingError,
            ) as e:
                wait = min(60, 5 * attempt + random.uniform(0, 3))
                print(
                    f"Request failed on {doc_id}: {type(e).__name__}. "
                    f"Retry {attempt}/3 after {wait:.1f}s",
                    flush=True,
                )
                time.sleep(wait)

            except requests.exceptions.HTTPError as e:
                status = e.response.status_code if e.response else None
                print(f"HTTP error on {doc_id}: status={status}", flush=True)
                break

            except zipfile.BadZipFile:
                print(f"Invalid ZIP file for {doc_id}, skipping...", flush=True)
                break

        if not success:
            failed_doc_ids.append(doc_id)
            consecutive_failures += 1
            print(f"Failed after retries, skipping {doc_id}", flush=True)

        if consecutive_failures >= max_consecutive_failures:
            print(
                f"Stopping early because {consecutive_failures} documents failed in a row. "
                "EDINET may be throttling or closing Cloud Run connections.",
                flush=True,
            )
            break

        time.sleep(2)

    if failed_doc_ids:
        failed_text = "\n".join(failed_doc_ids) + "\n"
        failed_path = f"raw/documents/{start_date}/failed_doc_ids.txt"

        failed_blob = bucket.blob(failed_path)
        failed_blob.upload_from_string(
            failed_text,
            content_type="text/plain",
        )

        print(f"Uploaded failed doc IDs to GCS: {failed_path}", flush=True)

    return failed_doc_ids