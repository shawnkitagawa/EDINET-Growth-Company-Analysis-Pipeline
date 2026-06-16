import os

API_KEY = os.getenv("EDINET_API_KEY")
URL_METADATA = os.getenv("EDINET_URL_METADATA", "https://api.edinet-fsa.go.jp/api/v2/documents.json")
URL_DOWNLOAD = os.getenv("EDINET_URL_DOWNLOAD", "https://api.edinet-fsa.go.jp/api/v2/documents")
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")


def require_config():
    missing = []

    if not API_KEY:
        missing.append("EDINET_API_KEY")

    if not BUCKET_NAME:
        missing.append("GCS_BUCKET_NAME")

    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")