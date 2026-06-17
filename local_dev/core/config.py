import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = DATA_DIR / "output"

DOCUMENTS_DIR = RAW_DIR / "documents"
METADATA_DIR = RAW_DIR / "metadata"
REFERENCE_DIR = RAW_DIR / "reference"

ANNUAL_REPORT_CSV_DIR = DOCUMENTS_DIR

DB_PATH = PROCESSED_DIR / "edinet.duckdb"
METADATA_CSV_PATH = METADATA_DIR / "csv"
EDINET_CODE_LIST_PATH = REFERENCE_DIR / "EdinetcodeDlInfo.csv"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)
REFERENCE_DIR.mkdir(parents=True, exist_ok=True)

API_KEY = os.getenv("EDINET_API_KEY")

URL_METADATA = "https://api.edinet-fsa.go.jp/api/v2/documents.json"
URL_DOWNLOAD = "https://api.edinet-fsa.go.jp/api/v2/documents"