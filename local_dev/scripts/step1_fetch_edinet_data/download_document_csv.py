import requests 
from core.config import API_KEY, URL_DOWNLOAD
import time 
from pathlib import Path 
import zipfile 
from io import BytesIO
import json 

 
def save_documents_to_csv(json_path: str, start_date: str, end_date: str):

    with open(json_path, "r", encoding = "utf-8") as f: 
        document_informations = json.load(f) 

    print(f"Loaded {len(document_informations)} documents")


    if len(document_informations) == 0:
        raise ValueError("Requires document_information before turning into CSV")

    params = {
        "type": 5,
        "Subscription-Key": API_KEY
    }


    data_range_name = f"{start_date}_to_{end_date}"

    data_dir = Path("data/raw/documents")/data_range_name
    data_dir.mkdir(parents=True, exist_ok=True)

    for document in document_informations:
        doc_id = document["docID"]
        output_path = data_dir / f"{doc_id}.csv"

        if output_path.exists():
            print(f"Already exists, skipping: {output_path}")
            continue

        for attempt in range(1, 4):
            try:
                url = f"{URL_DOWNLOAD}/{doc_id}"

                response = requests.get(
                    url,
                    params=params,
                    timeout=(5, 30)
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
                        print(f"No ASR CSV found for {doc_id}")
                        break

                    selected_csv = asr_files[0]

                    with z.open(selected_csv) as source:
                        with open(output_path, "wb") as target:
                            target.write(source.read())

                    print(f"Saved {selected_csv} as {output_path}")

                break

            except requests.exceptions.Timeout:
                print(f"Timeout on {doc_id}. Retry {attempt}/3")
                time.sleep(2)

            except requests.exceptions.RequestException as e:
                print(f"Request failed on {doc_id}: {e}. Retry {attempt}/3")
                time.sleep(2)

            except zipfile.BadZipFile:
                print(f"Invalid ZIP file for {doc_id}, skipping...")
                break
    