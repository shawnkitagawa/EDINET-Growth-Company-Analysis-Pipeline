import requests 
from core.config import API_KEY, URL_METADATA
from datetime import datetime, timedelta, date
from scripts.fetch_edinet_data.filter_documents import filter_documents, get_unique_documents_by_company
from scripts.fetch_edinet_data.save_metadata import save_document_metadata
import time 



def run_edinet_metadata_pipeline(start_date: str, date_length: int, file_name: str):

    if not API_KEY:
        raise ValueError("EDINET_API_KEY is not set. Please check your .env file.")

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("start date must be a valid date in YYYY-MM-DD format.")

    today = date.today()
    end_date = start + timedelta(days=date_length - 1)

    if end_date > today:
        end_date = today

    all_filtered_documents, updated_filtered_documents = fetch_all_edinet_documents(
        start=start,
        date_length=date_length
    )

    unique_company_document_information = get_unique_documents_by_company(
        all_filtered_documents,
        updated_filtered_documents
    )

    # if len(unique_company_document_information) == 0:
    #     raise ValueError(
    #         "No annual report documents were found after filtering. "
    #         "Please check the EDINET_API_KEY, target date range, and document filters."
    #     )

    if len(unique_company_document_information) == 0:
        print(
            "No annual report documents were found after filtering. "
            "This can be normal for a daily scheduled run. Exiting successfully.",
            flush=True,
        )
        return



    save_document_metadata(
        documents=unique_company_document_information,
        start_date=start_date,
        end_date=str(end_date),
        file_name = file_name
    )

    return unique_company_document_information


def fetch_all_edinet_documents(start: date, date_length: int) -> tuple[list[dict], list[dict]]:
    all_filtered_documents: list[dict] = []
    updated_filtered_documents: list[dict] = []

    today = date.today()

    for i in range(date_length):
        target_date = start + timedelta(days=i)

        if target_date > today:
            break

        date_str = target_date.strftime("%Y-%m-%d")

        print(f"-------------------------{date_str}-------------------------")

        results = fetch_current_date_documents(date_str=date_str)

        if not results:
            print(f"Skipped {date_str}")
            continue

        normal_docs, correction_docs = filter_documents(results=results, date_str=date_str)

        all_filtered_documents.extend(normal_docs)
        updated_filtered_documents.extend(correction_docs)

        print(f"Total documents: {len(all_filtered_documents)}")
        time.sleep(0.5)

    return all_filtered_documents, updated_filtered_documents


def fetch_current_date_documents(date_str: str) -> list[dict]:

    if not API_KEY:
        raise ValueError("EDINET_API_KEY is not set. Please check your .env file.")

    params = {
        "date": date_str,
        "type": 2,
        "Subscription-Key": API_KEY,
    }

    data = None

    for attempt in range(1, 4):
        try:
            response = requests.get(
                URL_METADATA,
                params=params,
                timeout=(5, 10)
            )

            if response.status_code in [401, 403]:
                raise ValueError(
                    "EDINET API authentication failed. "
                    "Please check whether EDINET_API_KEY is correct."
                )

            response.raise_for_status()
            data = response.json()
            break

        except requests.exceptions.Timeout:
            print(f"Timeout on {date_str}. Retry {attempt}/3")
            time.sleep(2)

        except requests.exceptions.HTTPError as e:
            print(f"Request failed on {date_str}: {e}. Retry {attempt}/3")
            time.sleep(2)

        except requests.exceptions.RequestException as e:
            print(f"Request failed on {date_str}: {e}. Retry {attempt}/3")
            time.sleep(2)

        except ValueError as e:
            if "EDINET API authentication failed" in str(e):
                raise

            print(f"Invalid JSON on {date_str}, skipping...")
            break

    if data is None:
        return []

    return data.get("results", [])