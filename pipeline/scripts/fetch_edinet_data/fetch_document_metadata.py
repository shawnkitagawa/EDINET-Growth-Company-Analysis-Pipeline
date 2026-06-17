import time
import requests
from datetime import datetime, timedelta, date

from pipeline.core.config import get_api_key, URL_METADATA
from pipeline.core.storage import upload_document_metadata_csv_to_gcs
from pipeline.scripts.fetch_edinet_data.filter_documents import (
    filter_documents,
    get_unique_documents_by_company,
)


def fetch_current_date_documents(
    date_str: str,
    request_get=requests.get,
    api_key: str = get_api_key(),
    url_metadata: str = URL_METADATA,
    sleep_func=time.sleep,
) -> list[dict]:
    if not api_key:
        raise ValueError("EDINET_API_KEY is not set.")

    if not url_metadata:
        raise ValueError("URL_METADATA is not set.")

    params = {
        "date": date_str,
        "type": 2,
        "Subscription-Key": api_key,
    }

    data = None

    for attempt in range(1, 4):
        try:
            response = request_get(
                url_metadata,
                params=params,
                timeout=(5, 10),
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
            sleep_func(2)

        except requests.exceptions.HTTPError as e:
            print(f"Request failed on {date_str}: {e}. Retry {attempt}/3")
            sleep_func(2)

        except requests.exceptions.RequestException as e:
            print(f"Request failed on {date_str}: {e}. Retry {attempt}/3")
            sleep_func(2)

        except ValueError as e:
            if "EDINET API authentication failed" in str(e):
                raise

            print(f"Invalid JSON on {date_str}, skipping...")
            break

    if data is None:
        return []

    return data.get("results", [])


def fetch_all_edinet_documents(
    start: date,
    date_length: int,
    fetch_current_date_func=fetch_current_date_documents,
    filter_documents_func=filter_documents,
    today_func=date.today,
    sleep_func=time.sleep,
) -> tuple[list[dict], list[dict]]:
    all_filtered_documents: list[dict] = []
    updated_filtered_documents: list[dict] = []

    today = today_func()

    for i in range(date_length):
        target_date = start + timedelta(days=i)

        if target_date > today:
            break

        date_str = target_date.strftime("%Y-%m-%d")

        print(f"-------------------------{date_str}-------------------------")

        results = fetch_current_date_func(date_str=date_str)

        if not results:
            print(f"Skipped {date_str}")
            continue

        normal_docs, correction_docs = filter_documents_func(
            results=results,
            date_str=date_str,
        )

        all_filtered_documents.extend(normal_docs)
        updated_filtered_documents.extend(correction_docs)

        print(f"Total documents: {len(all_filtered_documents)}")
        sleep_func(0.5)

    return all_filtered_documents, updated_filtered_documents


def run_edinet_metadata_pipeline(
    start_date: str,
    date_length: int,
    file_name: str,
    api_key: str = API_KEY,
    fetch_all_documents_func=fetch_all_edinet_documents,
    get_unique_documents_func=get_unique_documents_by_company,
    upload_metadata_func=upload_document_metadata_csv_to_gcs,
    today_func=date.today,
):
    if not api_key:
        raise ValueError("EDINET_API_KEY is not set. Please check your .env file.")

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("start date must be a valid date in YYYY-MM-DD format.")

    if date_length <= 0:
        raise ValueError("date_length must be greater than 0.")

    today = today_func()
    end_date = start + timedelta(days=date_length - 1)

    if end_date > today:
        end_date = today

    all_filtered_documents, updated_filtered_documents = fetch_all_documents_func(
        start=start,
        date_length=date_length,
    )

    unique_company_document_information = get_unique_documents_func(
        all_filtered_documents,
        updated_filtered_documents,
    )

    if len(unique_company_document_information) == 0:
        print(
            "No annual report documents were found after filtering. "
            "This can be normal for a daily scheduled run. Exiting successfully.",
            flush=True,
        )
        return []

    upload_metadata_func(
        documents=unique_company_document_information,
        file_name=file_name,
    )

    return unique_company_document_information