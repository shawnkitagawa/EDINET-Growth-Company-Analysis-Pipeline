import pandas as pd 
from pathlib import Path 


def detect_encoding(path: Path) -> str:
    with open(path, "rb") as f:
        raw = f.read(4)

    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return "utf-16"

    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"

    return "cp932"


def read_japanese_table(path: str | Path, **kwargs) -> pd.DataFrame:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    encoding = kwargs.pop("encoding", None) or detect_encoding(path)

    return pd.read_csv(
        path,
        encoding=encoding,
        **kwargs
    )

def print_table_counts(con, table_names):
    print("\n=== Row counts ===")

    queries = [
        f"SELECT '{table_name}' AS table_name, COUNT(*) AS row_count FROM {table_name}"
        for table_name in table_names
    ]

    result = con.execute("\nUNION ALL\n".join(queries)).fetchdf()
    print(result)


def check_duplicates(con):
    print("\n=== Duplicate companies in finalized_annual_report_metadata ===")

    duplicates = con.execute("""
        SELECT
            edinetCode,
            filerName,
            COUNT(*) AS row_count
        FROM finalized_annual_report_metadata
        GROUP BY edinetCode, filerName
        HAVING COUNT(*) > 1
        ORDER BY row_count DESC;
    """).fetchdf()

    print(duplicates)

    print("\n=== Missing period dates in finalized_annual_report_metadata ===")

    missing_periods = con.execute("""
        SELECT *
        FROM finalized_annual_report_metadata
        WHERE periodStart IS NULL
           OR periodEnd IS NULL;
    """).fetchdf()

    print(missing_periods)
