# tests/pipeline/test_metadata_pipeline.py

from datetime import date

import pytest
import requests

from pipeline.scripts.fetch_edinet_data.fetch_document_metadata import (
    fetch_current_date_documents,
    fetch_all_edinet_documents,
    run_edinet_metadata_pipeline,
)


class FakeResponse:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json_data = json_data or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._json_data


def test_fetch_current_date_documents_returns_results():
    def fake_request_get(url, params, headers, timeout):
        assert headers["User-Agent"] == "edinet-growth-pipeline/1.0"
        assert headers["Connection"] == "close"

        return FakeResponse(
            status_code=200,
            json_data={
                "results": [
                    {"docID": "S100TEST", "docDescription": "有価証券報告書"}
                ]
            },
        )

    result = fetch_current_date_documents(
        date_str="2026-06-15",
        request_get=fake_request_get,
        api_key="fake-api-key",
        url_metadata="https://fake-edinet-api.example.com",
        sleep_func=lambda seconds: None,
    )

    assert result == [
        {"docID": "S100TEST", "docDescription": "有価証券報告書"}
    ]


def test_fetch_current_date_documents_returns_empty_list_when_no_data_after_timeout():
    def fake_request_get(url, params, headers, timeout):
        assert headers["User-Agent"] == "edinet-growth-pipeline/1.0"
        assert headers["Connection"] == "close"

        raise requests.exceptions.Timeout()

    result = fetch_current_date_documents(
        date_str="2026-06-15",
        request_get=fake_request_get,
        api_key="fake-api-key",
        url_metadata="https://fake-edinet-api.example.com",
        sleep_func=lambda seconds: None,
    )

    assert result == []


def test_fetch_current_date_documents_raises_error_for_auth_failure():
    def fake_request_get(url, params, headers, timeout):
        assert headers["User-Agent"] == "edinet-growth-pipeline/1.0"
        assert headers["Connection"] == "close"

        return FakeResponse(status_code=403, json_data={})

    with pytest.raises(ValueError, match="EDINET API authentication failed"):
        fetch_current_date_documents(
            date_str="2026-06-15",
            request_get=fake_request_get,
            api_key="fake-api-key",
            url_metadata="https://fake-edinet-api.example.com",
            sleep_func=lambda seconds: None,
        )


def test_fetch_all_edinet_documents_collects_normal_and_correction_documents():
    def fake_fetch_current_date_func(date_str):
        return [
            {"docID": f"{date_str}-NORMAL"},
            {"docID": f"{date_str}-CORRECTION"},
        ]

    def fake_filter_documents_func(results, date_str):
        normal_docs = [doc for doc in results if "NORMAL" in doc["docID"]]
        correction_docs = [doc for doc in results if "CORRECTION" in doc["docID"]]
        return normal_docs, correction_docs

    normal_docs, correction_docs = fetch_all_edinet_documents(
        start=date(2026, 6, 14),
        date_length=2,
        fetch_current_date_func=fake_fetch_current_date_func,
        filter_documents_func=fake_filter_documents_func,
        today_func=lambda: date(2026, 6, 15),
        sleep_func=lambda seconds: None,
    )

    assert normal_docs == [
        {"docID": "2026-06-14-NORMAL"},
        {"docID": "2026-06-15-NORMAL"},
    ]

    assert correction_docs == [
        {"docID": "2026-06-14-CORRECTION"},
        {"docID": "2026-06-15-CORRECTION"},
    ]


def test_fetch_all_edinet_documents_stops_when_target_date_is_future():
    called_dates = []

    def fake_fetch_current_date_func(date_str):
        called_dates.append(date_str)
        return [{"docID": f"{date_str}-NORMAL"}]

    def fake_filter_documents_func(results, date_str):
        return results, []

    normal_docs, correction_docs = fetch_all_edinet_documents(
        start=date(2026, 6, 15),
        date_length=3,
        fetch_current_date_func=fake_fetch_current_date_func,
        filter_documents_func=fake_filter_documents_func,
        today_func=lambda: date(2026, 6, 16),
        sleep_func=lambda seconds: None,
    )

    assert called_dates == ["2026-06-15", "2026-06-16"]
    assert normal_docs == [
        {"docID": "2026-06-15-NORMAL"},
        {"docID": "2026-06-16-NORMAL"},
    ]
    assert correction_docs == []


def test_run_edinet_metadata_pipeline_uploads_metadata_when_documents_exist():
    uploaded = {}

    def fake_fetch_all_documents_func(start, date_length, fetch_current_date_func=None):
        normal_docs = [
            {
                "docID": "S100TEST",
                "edinetCode": "E12345",
                "filerName": "Test Company",
                "docDescription": "有価証券報告書",
            }
        ]
        correction_docs = []
        return normal_docs, correction_docs

    def fake_get_unique_documents_func(normal_docs, correction_docs):
        return normal_docs

    def fake_upload_metadata_func(documents, file_name):
        uploaded["documents"] = documents
        uploaded["file_name"] = file_name

    result = run_edinet_metadata_pipeline(
        start_date="2026-06-15",
        date_length=1,
        file_name="edinet_documents_2026-06-15",
        api_key="fake-api-key",
        fetch_all_documents_func=fake_fetch_all_documents_func,
        get_unique_documents_func=fake_get_unique_documents_func,
        upload_metadata_func=fake_upload_metadata_func,
        today_func=lambda: date(2026, 6, 15),
    )

    assert result == [
        {
            "docID": "S100TEST",
            "edinetCode": "E12345",
            "filerName": "Test Company",
            "docDescription": "有価証券報告書",
        }
    ]

    assert uploaded["file_name"] == "edinet_documents_2026-06-15"
    assert uploaded["documents"][0]["docID"] == "S100TEST"


def test_run_edinet_metadata_pipeline_does_not_upload_when_no_documents():
    upload_called = False

    def fake_fetch_all_documents_func(start, date_length, fetch_current_date_func=None):
        return [], []

    def fake_get_unique_documents_func(normal_docs, correction_docs):
        return []

    def fake_upload_metadata_func(documents, file_name):
        nonlocal upload_called
        upload_called = True

    result = run_edinet_metadata_pipeline(
        start_date="2026-06-15",
        date_length=1,
        file_name="edinet_documents_2026-06-15",
        api_key="fake-api-key",
        fetch_all_documents_func=fake_fetch_all_documents_func,
        get_unique_documents_func=fake_get_unique_documents_func,
        upload_metadata_func=fake_upload_metadata_func,
        today_func=lambda: date(2026, 6, 15),
    )

    assert result == []
    assert upload_called is False


def test_run_edinet_metadata_pipeline_rejects_invalid_start_date():
    with pytest.raises(ValueError, match="start date must be a valid date"):
        run_edinet_metadata_pipeline(
            start_date="bad-date",
            date_length=1,
            file_name="edinet_documents_bad",
            api_key="fake-api-key",
        )


def test_run_edinet_metadata_pipeline_rejects_invalid_date_length():
    with pytest.raises(ValueError, match="date_length must be greater than 0"):
        run_edinet_metadata_pipeline(
            start_date="2026-06-15",
            date_length=0,
            file_name="edinet_documents_2026-06-15",
            api_key="fake-api-key",
        )