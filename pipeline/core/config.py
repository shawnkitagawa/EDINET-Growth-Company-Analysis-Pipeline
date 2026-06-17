import os
from google.cloud import secretmanager

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
EDINET_API_KEY_SECRET_NAME = os.getenv("EDINET_API_KEY_SECRET_NAME")
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

URL_METADATA = "https://disclosure.edinet-fsa.go.jp/api/v2/documents.json"
URL_DOWNLOAD = "https://disclosure.edinet-fsa.go.jp/api/v2/documents"

def require_config():
    missing = []

    if not GCP_PROJECT_ID:
        missing.append("GCP_PROJECT_ID")
    if not EDINET_API_KEY_SECRET_NAME:
        missing.append("EDINET_API_KEY_SECRET_NAME")
    if not BUCKET_NAME:
        missing.append("GCS_BUCKET_NAME")

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

def get_secret(project_id: str, secret_id: str, version_id: str = "latest") -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

def get_api_key() -> str:
    require_config()
    return get_secret(
        project_id=GCP_PROJECT_ID,
        secret_id=EDINET_API_KEY_SECRET_NAME,
    )