from pathlib import Path 
import json 
import pandas as pd 
 

def save_document_metadata(documents: list[dict], start_date: str, end_date: str,file_name: str, output_dir: str = "data/raw/metadata"):
    
    json_dir = Path(f"{output_dir}/json")
    csv_dir = Path(f"{output_dir}/csv")

    json_dir.mkdir(parents=True, exist_ok=True)
    csv_dir.mkdir(parents=True, exist_ok=True)


    # filename = f"edinet_documents_{start_date}_to_{end_date}"

    json_path = json_dir / f"{file_name}.json"
    csv_path = csv_dir / f"{file_name}.csv"


    with open(json_path, "w", encoding = "utf-8") as f: 
        json.dump(documents, f , ensure_ascii=False, indent = 2)

    pd.DataFrame(documents).to_csv(
        csv_path, 
        index = False, 
        encoding = "utf-8-sig"
    )

    print(f"Saved JSON: {json_path}")
    print(f"Saved CSV: {csv_path}")