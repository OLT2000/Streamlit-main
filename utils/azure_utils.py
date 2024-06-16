from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

import os, uuid
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

load_dotenv()
ACCESS_KEY = os.getenv("STORAGE_ACCESS_KEY")
ACCOUNT_URL = os.getenv("STORAGE_ACCESS_URL")
CONTAINER_NAME = os.getenv("TEMPLATE_CONTAINER_NAME")

def setup_blob_client():
    try:
        # Create the BlobServiceClient object
        blob_service_client = BlobServiceClient(ACCOUNT_URL, credential=ACCESS_KEY)

    except Exception as ex:
        print('Exception:')
        print(ex)

    return blob_service_client


def get_container_client(container_name: str, blob_service_client):
    try:
        container_client = blob_service_client.get_container_client(container_name)

    except Exception as e:
        print(f"An unexpected error occurred when loading container '{container_name}': {e}")

    else: 
        return container_client
    

def get_ppt_template_names(verbose: bool = False):
    blob_service_client = setup_blob_client()
    container_client = get_container_client("charter-templates", blob_service_client=blob_service_client)

    if verbose:
        print("Found the following templates:")
        for blob_name in container_client.list_blob_names():
            print(f"\t- {blob_name}")

    return container_client.list_blob_names()


def get_ppt_template_files(verbose: bool = False):
    blob_service_client = setup_blob_client()
    container_client = get_container_client("charter-templates", blob_service_client=blob_service_client)

    if verbose:
        print("Found the following templates:")
        for blob_name in container_client.list_blob_names():
            print(f"\t- {blob_name}")

    return container_client.list_blobs()


def download_blob(blob_name: str):
    try:
        


if __name__ == "__main__":
    blob_service_client = setup_blob_client()
    container_client = get_container_client("charter-templates", blob_service_client=blob_service_client)