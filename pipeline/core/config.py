import os
from google.cloud import secretmanager


URL_METADATA = "https://api.edinet-fsa.go.jp/api/v2/documents.json",
URL_DOWNLOAD = "https://api.edinet-fsa.go.jp/api/v2/documents",

BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
EDINET_API_KEY_SECRET_NAME = os.getenv("EDINET_API_KEY_SECRET_NAME")


def get_secret(project_id: str, secret_name: str) -> str:
    client = secretmanager.SecretManagerServiceClient()

    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"

    response = client.access_secret_version(request={"name": name})

    return response.payload.data.decode("UTF-8")


def require_config():
    missing = []

    if not PROJECT_ID:
        missing.append("GCP_PROJECT_ID")

    if not EDINET_API_KEY_SECRET_NAME:
        missing.append("EDINET_API_KEY_SECRET_NAME")

    if not BUCKET_NAME:
        missing.append("GCS_BUCKET_NAME")

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

require_config()

API_KEY = get_secret(
    project_id=PROJECT_ID,
    secret_name=EDINET_API_KEY_SECRET_NAME,
)