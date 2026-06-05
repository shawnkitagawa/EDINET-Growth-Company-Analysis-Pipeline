from pathlib import Path 
from google.cloud import storage

def upload_file_to_gcs(local_path: str, bucket_name: str, destination_path:str) -> None: 
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_path)

    blob.upload_from_filename(local_path)


def upload_folder_to_gcs(local_folder: str, bucket_name: str, destination_prefix: str) -> None: 
    folder = Path(local_folder)

    for file_path in folder.rglob("*"): 
        if file_path.is_file(): 
            relative_path = file_path.relative_to(folder)
            destination_path = f"{destination_prefix}/{relative_path}".replace("\\", "/")

            upload_file_to_gcs(
                local_path=str(file_path),
                bucket_name=bucket_name,
                destination_path=destination_path,
            )



