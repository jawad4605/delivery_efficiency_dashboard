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
        "type": "service_account",
        "project_id": "dataoperations-449123",
        "private_key_id": "3b5b6be3c2719d1690f64e9fceae58eecb1c58d3",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCnkZMFK8qv3V2G\nOEs1iz/WgMXcWLenFMTWEzBAw2runG4t1x462TQ0uA2BIe8OcdgX0yebsLeKR3xC\nKyJg7hT9jmng7mrx4ZyJowu24PBiCJpugyijvTC6VyCsz9z7G2ZXGN0GUFFI666M\n6BxnVG3KXV0YbP63fv0WEAMPyXgbmGWJ4qet3baeKRCHbRqEpdV/vh8cGNagO3sw\n2l0SrN2sYgTzzYg4qVnpyl2pzn2DNqWqhG7xspwMLYvxjZ+W96K4yz3SKXHvjHom\nwHzLCX52bFsYVaRsBTztE562++cRJi8HKAxZcpNDKhpyJpsfKM7+uMgPoDO2U3Do\nYk3S3OCNAgMBAAECggEATMpAdqEv3FH0dvq7NIlgstsGUUjyuIWjAnt+pF8pVLmp\nICaxusQo0XP69E9prtPq9FgWkZl1MtA5mFUOBx9zzRKDYMnBhqEeTFDEoIUKg9Jv\neu9uI0Mi3nHpDmifWw+eYZGKUEdkSKeAsR/5TDz7pz4L2JKyU8LFFmQ2Evj/qpz3\nkkr4mozIw/Ed+z5MKLAo04hxtak9GvNoXccbOJQ176na8LYfgOD6d4F8v8qidjy1\nqTwGTIPHKd0AFfCUMh2JZAHpFDuu2Z4rdhnG4kU6OSGGjwVwt/2Y2AEJKlsK10C+\nwUTjdVbpwL+v4eQg+np4gPNMdegFrmx238p/uZvtnQKBgQDr6fgGmZz/B2g/hdav\n6MbzxeDR5tEyrrTcg0ZhP/8qhl8s4/80w25n7FJZ4ncuf3WjS5+ZMo3E3xO34xBb\nTenxU6cLrkCRqPUb9wxeZA9Iyd/z9XcINVm3LjxkSYCpQ7Yprm4TKuUB9XxNKNjm\ntrMcHqhLgVNYDXsT1kXhvr17IwKBgQC11e/N3AriuyA7+GNJTCBVM+QgkTg9VscO\n6VGFvBhJmO7Q6fEnLzo3wSu0xIq7RR9ptzI8iE8C49yVittRpR9+xEQklgE+z/jD\nEKhFRWaLgdh2/HGOklEgligrl7dBxarRrsmQ5dcpo1C7YZAH3pS3sjuWtKMJ7H1z\n+PHzkOQIjwKBgQC6IFwZCPU+mJ99DqE1JFhjWAlqUctXS1NSbxgF/jHZYS6SAkgF\nXvMqdt76H5ycSN+NOErw2VvUqZOrDzCGeNBMIA25P3+d7EmGCMHvbs5IRU218kI5\nba4cwhPPo9YotU1xUTdzU/JeO0oYrlOCoz5ovx9UgvI4lFo4amO0GYLxNQKBgQCd\nEqUHyuCMYuDBbRs3Ic98Skrx5wAR3HgvZVTKlWTVjoodZTivhJhhuTgr+utsQZWV\nGG8I4yZ9dKADfeNeb6j5NEk44WtJ+xUES8tPq1edgxieEAt4AOSbpZolrfTbmAir\nALWVuTVX/n+qnehxI9CLribTVE7SL7tfBtjacXrJ+QKBgQC6P8EJpTk91G0sE2BA\nvYwOSNnEA1DRGMIxqd+oihA5ZOD3Z+iOprGa5YJ3nsZ8JJ6hD7ucJ/F4Mq4sJOCi\nDx6ZQNrC89ycGKg28ocLtKrmyvohPo39lb23Tp7IxdHKwHDjiJViNtAbeV9avwPz\nfMNyh6agcYspcDuc1wBAZh5rNA==\n-----END PRIVATE KEY-----\n",
        "client_email": "coding-evaluation@dataoperations-449123.iam.gserviceaccount.com",
        "client_id": "112271742990232659742",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/coding-evaluation%40dataoperations-449123.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
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