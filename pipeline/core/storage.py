import csv
from pathlib import Path 
from google.cloud import storage
from core.config import BUCKET_NAME
from io import StringIO 
import csv


def upload_document_metadata_csv_to_gcs(
    documents: list[dict],
    file_name: str,
) -> str:
    if not documents:
        raise ValueError("No documents to upload.")

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    destination_path = f"raw/metadata/csv/{file_name}.csv"

    output = StringIO()

    fieldnames = documents[0].keys()

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(documents)

    blob = bucket.blob(destination_path)
    blob.upload_from_string(
        output.getvalue(),
        content_type="text/csv",
    )

    print(f"Uploaded metadata CSV to GCS: gs://{BUCKET_NAME}/{destination_path}", flush=True)

    return destination_path




