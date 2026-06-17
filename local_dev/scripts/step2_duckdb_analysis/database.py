import duckdb
from core.config import PROCESSED_DIR, DB_PATH
from pathlib import Path

def connect_db():
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    return duckdb.connect(DB_PATH)
