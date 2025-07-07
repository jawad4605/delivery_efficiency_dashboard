import json
from google.cloud import storage
from google.oauth2 import service_account
import os

def upload_file_to_gcs(file_path, bucket_name, destination_blob_name, credentials):
    """
    Uploads a file from the local filesystem to a specified GCS bucket using service account credentials.
    """
    if isinstance(credentials, str):
        credentials = json.loads(credentials)
    creds = service_account.Credentials.from_service_account_info(credentials)
    client = storage.Client(credentials=creds, project=credentials.get("project_id"))
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    try:
        blob.upload_from_filename(file_path)
        print(f"Uploaded: {file_path} -> gs://{bucket_name}/{destination_blob_name}")
    except Exception as e:
        print("Error uploading file:", e)

def upload_directory_to_gcs(local_dir, bucket_name, gcs_dir, credentials):
        """
        Recursively uploads a directory to GCS under the specified gcs_dir.
        Only uploads files with allowed extensions.
        """
        allowed_exts = {'.py', '.html', '.csv', '.png', '.npy'}
        for root, _, files in os.walk(local_dir):
            for file in files:
                if os.path.splitext(file)[1].lower() not in allowed_exts:
                    continue
                local_path = os.path.join(root, file)
                rel_path = os.path.relpath(local_path, local_dir)
                gcs_path = os.path.join(gcs_dir, rel_path).replace("\\", "/")
                upload_file_to_gcs(local_path, bucket_name, gcs_path, credentials)

if __name__ == "__main__":
    while True:
        data_row_id = input("Enter the Data Row ID (example: cmab3kuzr208x5641vpld9tq42): ").strip()
        if data_row_id.startswith("cm") and data_row_id.isalnum():
            break
        print("Invalid Data Row ID. It must start with 'cm' and contain only letters and numbers.")

    print("\nPlease confirm that all files in your 'data', 'outputs', and 'scripts' folders are correct.")
    print("Once uploaded, you will \033[91mNOT\033[0m be able to update or replace them.")
    confirm = input("Type 'yes' to continue with the upload, or anything else to cancel: ").strip().lower()
    if confirm != 'yes':
        print("Upload cancelled.")
        exit(0)
    bucket_name = 'coding_evaluation'
    credentials = {

    }

    base_dir = os.path.dirname(os.path.abspath(__file__))
    folders = {
        "data": os.path.abspath(os.path.join(base_dir, "data")),
        "outputs": os.path.abspath(os.path.join(base_dir, "outputs")),
        "scripts": os.path.abspath(os.path.join(base_dir, "scripts")),
    }

    # Upload each folder
    for key, local_path in folders.items():
        gcs_dir = f"{data_row_id}/{key}/"
        if os.path.exists(local_path):
            upload_directory_to_gcs(local_path, bucket_name, gcs_dir, credentials)
        else:
            print(f"Warning: {local_path} does not exist, skipping.")

    print("\nCopy-paste the following into the Labelbox editor:\n")
    print(f"data_gen.py URI: gs://{bucket_name}/{data_row_id}/scripts/data_gen.py")
    print(f"Generated Data URI: gs://{bucket_name}/{data_row_id}/data/")
    print(f"viz.py URI: gs://{bucket_name}/{data_row_id}/scripts/viz.py")
    print(f"Outputs URI: gs://{bucket_name}/{data_row_id}/outputs/")
