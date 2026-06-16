from io import BytesIO
import zipfile

import pytest
import requests

from pipeline.scripts.fetch_edinet_data.download_document_csv import (
    download_document_csvs_to_gcs,
)


class FakeBlob:
    def __init__(self, exists_result=False):
        self.exists_result = exists_result
        self.uploaded_file_content = None
        self.uploaded_string_content = None
        self.content_type = None

    def exists(self):
        return self.exists_result

    def upload_from_file(self, source, content_type=None, timeout=None):
        self.uploaded_file_content = source.read()
        self.content_type = content_type
        self.timeout = timeout

    def upload_from_string(self, data, content_type=None):
        self.uploaded_string_content = data
        self.content_type = content_type


class FakeBucket:
    def __init__(self):
        self.blobs = {}

    def blob(self, path):
        if path not in self.blobs:
            self.blobs[path] = FakeBlob()
        return self.blobs[path]


class FakeStorageClient:
    def __init__(self, bucket):
        self.fake_bucket = bucket

    def bucket(self, bucket_name):
        return self.fake_bucket


class FakeResponse:
    def __init__(self, status_code=200, content=b""):
        self.status_code = status_code
        self.content = content
        self.response = self

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(response=self)


def make_test_zip_with_asr_csv():
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as z:
        z.writestr("XBRL_TO_CSV/asr_test.csv", "docID,value\nS100TEST,100\n")
        z.writestr("XBRL_TO_CSV/other.csv", "other,data\n")

    return zip_buffer.getvalue()


def make_test_zip_without_asr_csv():
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as z:
        z.writestr("XBRL_TO_CSV/other.csv", "other,data\n")

    return zip_buffer.getvalue()


def test_download_document_csvs_to_gcs_uploads_asr_csv(monkeypatch):
    fake_bucket = FakeBucket()

    def fake_storage_client():
        return FakeStorageClient(fake_bucket)

    def fake_requests_get(url, params, headers, timeout):
        return FakeResponse(
            status_code=200,
            content=make_test_zip_with_asr_csv(),
        )

    monkeypatch.setattr(
        "pipeline.scripts.fetch_edinet_data.download_document_csvs_to_gcs.storage.Client",
        fake_storage_client,
    )

    monkeypatch.setattr(
        "pipeline.scripts.fetch_edinet_data.download_document_csvs_to_gcs.requests.get",
        fake_requests_get,
    )

    monkeypatch.setattr(
        "pipeline.scripts.fetch_edinet_data.download_document_csvs_to_gcs.time.sleep",
        lambda seconds: None,
    )

    result = download_document_csvs_to_gcs(
        document_informations=[{"docID": "S100TEST"}],
        start_date="2026-06-15",
    )

    expected_path = "raw/documents/2026-06-15/S100TEST.csv"
    uploaded_blob = fake_bucket.blobs[expected_path]

    assert result == []
    assert uploaded_blob.uploaded_file_content == b"docID,value\nS100TEST,100\n"
    assert uploaded_blob.content_type == "text/csv"


def test_download_document_csvs_to_gcs_returns_empty_list_when_no_documents():
    result = download_document_csvs_to_gcs(
        document_informations=[],
        start_date="2026-06-15",
    )

    assert result == []


def test_download_document_csvs_to_gcs_skips_existing_blob(monkeypatch):
    fake_bucket = FakeBucket()
    existing_path = "raw/documents/2026-06-15/S100TEST.csv"
    fake_bucket.blobs[existing_path] = FakeBlob(exists_result=True)

    request_called = False

    def fake_storage_client():
        return FakeStorageClient(fake_bucket)

    def fake_requests_get(url, params, headers, timeout):
        nonlocal request_called
        request_called = True
        return FakeResponse(
            status_code=200,
            content=make_test_zip_with_asr_csv(),
        )

    monkeypatch.setattr(
        "pipeline.scripts.fetch_edinet_data.download_document_csvs_to_gcs.storage.Client",
        fake_storage_client,
    )

    monkeypatch.setattr(
        "pipeline.scripts.fetch_edinet_data.download_document_csvs_to_gcs.requests.get",
        fake_requests_get,
    )

    monkeypatch.setattr(
        "pipeline.scripts.fetch_edinet_data.download_document_csvs_to_gcs.time.sleep",
        lambda seconds: None,
    )

    result = download_document_csvs_to_gcs(
        document_informations=[{"docID": "S100TEST"}],
        start_date="2026-06-15",
    )

    assert result == []
    assert request_called is False


def test_download_document_csvs_to_gcs_does_not_fail_when_no_asr_csv(monkeypatch):
    fake_bucket = FakeBucket()

    def fake_storage_client():
        return FakeStorageClient(fake_bucket)

    def fake_requests_get(url, params, headers, timeout):
        return FakeResponse(
            status_code=200,
            content=make_test_zip_without_asr_csv(),
        )

    monkeypatch.setattr(
        "pipeline.scripts.fetch_edinet_data.download_document_csvs_to_gcs.storage.Client",
        fake_storage_client,
    )

    monkeypatch.setattr(
        "pipeline.scripts.fetch_edinet_data.download_document_csvs_to_gcs.requests.get",
        fake_requests_get,
    )

    monkeypatch.setattr(
        "pipeline.scripts.fetch_edinet_data.download_document_csvs_to_gcs.time.sleep",
        lambda seconds: None,
    )

    result = download_document_csvs_to_gcs(
        document_informations=[{"docID": "S100TEST"}],
        start_date="2026-06-15",
    )

    assert result == []

    expected_path = "raw/documents/2026-06-15/S100TEST.csv"
    assert fake_bucket.blobs[expected_path].uploaded_file_content is None


def test_download_document_csvs_to_gcs_records_failed_doc_id_on_http_error(monkeypatch):
    fake_bucket = FakeBucket()

    def fake_storage_client():
        return FakeStorageClient(fake_bucket)

    def fake_requests_get(url, params, headers, timeout):
        return FakeResponse(status_code=500, content=b"")

    monkeypatch.setattr(
        "pipeline.scripts.fetch_edinet_data.download_document_csvs_to_gcs.storage.Client",
        fake_storage_client,
    )

    monkeypatch.setattr(
        "pipeline.scripts.fetch_edinet_data.download_document_csvs_to_gcs.requests.get",
        fake_requests_get,
    )

    monkeypatch.setattr(
        "pipeline.scripts.fetch_edinet_data.download_document_csvs_to_gcs.time.sleep",
        lambda seconds: None,
    )

    result = download_document_csvs_to_gcs(
        document_informations=[{"docID": "S100FAIL"}],
        start_date="2026-06-15",
    )

    failed_path = "raw/documents/2026-06-15/failed_doc_ids.txt"
    failed_blob = fake_bucket.blobs[failed_path]

    assert result == ["S100FAIL"]
    assert failed_blob.uploaded_string_content == "S100FAIL\n"
    assert failed_blob.content_type == "text/plain"


def test_download_document_csvs_to_gcs_records_failed_doc_id_on_bad_zip(monkeypatch):
    fake_bucket = FakeBucket()

    def fake_storage_client():
        return FakeStorageClient(fake_bucket)

    def fake_requests_get(url, params, headers, timeout):
        return FakeResponse(
            status_code=200,
            content=b"this is not a zip file",
        )

    monkeypatch.setattr(
        "pipeline.scripts.fetch_edinet_data.download_document_csvs_to_gcs.storage.Client",
        fake_storage_client,
    )

    monkeypatch.setattr(
        "pipeline.scripts.fetch_edinet_data.download_document_csvs_to_gcs.requests.get",
        fake_requests_get,
    )

    monkeypatch.setattr(
        "pipeline.scripts.fetch_edinet_data.download_document_csvs_to_gcs.time.sleep",
        lambda seconds: None,
    )

    result = download_document_csvs_to_gcs(
        document_informations=[{"docID": "S100BADZIP"}],
        start_date="2026-06-15",
    )

    failed_path = "raw/documents/2026-06-15/failed_doc_ids.txt"
    failed_blob = fake_bucket.blobs[failed_path]

    assert result == ["S100BADZIP"]
    assert failed_blob.uploaded_string_content == "S100BADZIP\n"