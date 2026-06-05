import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("EDINET_API_KEY", "").strip()
if not API_KEY:
    raise ValueError("EDINET_API_KEY is not set.")

URL_METADATA = "https://api.edinet-fsa.go.jp/api/v2/documents.json"
URL_DOWNLOAD = "https://api.edinet-fsa.go.jp/api/v2/documents"