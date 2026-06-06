from pathlib import Path 
from google.cloud import storage
from core.config import BUCKET_NAME



def upload_folder_to_gcs(local_folder: str, destination_prefix: str) -> None:
    folder = Path(local_folder)

    if not folder.exists():
        raise FileNotFoundError(f"Local folder does not exist: {local_folder}")

    if not folder.is_dir():
        raise NotADirectoryError(f"Expected a folder, got: {local_folder}")

    files = [file_path for file_path in folder.rglob("*") if file_path.is_file()]

    print(f"Starting upload folder: {local_folder}", flush=True)
    print(f"Destination prefix: {destination_prefix}", flush=True)
    print(f"Found {len(files)} files to upload", flush=True)

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    for i, file_path in enumerate(files, start=1):
        relative_path = file_path.relative_to(folder)
        destination_path = f"{destination_prefix}/{relative_path}".replace("\\", "/")

        print(f"[{i}/{len(files)}] Uploading {file_path} -> {destination_path}", flush=True)

        blob = bucket.blob(destination_path)
        blob.upload_from_filename(str(file_path), timeout=120)

        print(f"[{i}/{len(files)}] Uploaded {destination_path}", flush=True)

    print(f"Finished uploading folder: {local_folder}", flush=True)



    


def upload_file_to_gcs(local_path: str, destination_path:str) -> None: 
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_path)

    blob.upload_from_filename(local_path)



