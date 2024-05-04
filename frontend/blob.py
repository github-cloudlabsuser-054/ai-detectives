import os
import dotenv
from azure.storage.blob import BlobServiceClient
import datetime

from langchain_community.document_loaders import AzureBlobStorageContainerLoader, TextLoader


envpath = os.path.abspath(r"frontend\\.env")
dotenv.load_dotenv(envpath)

storage_account_key=os.getenv("STORAGE_ACCOUNT_KEY")
storage_account_name=os.getenv("STORAGE_ACCOUNT_NAME")
connection_string=os.getenv("CONNECTION_STRING")


# Set up the connection to Azure Blob Storage
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_name = "emails"
container_client = blob_service_client.get_container_client(container_name)

def getDocuments(uploaded_files):
    
    # now = datetime.datetime.now()
    # # convert to string
    # date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    # folder_name = f"{datetime.datetime}-upload"
    # # Create a folder in the container
    # container_client.create_blob_directory(folder_name)
    # # Load the uploaded files as documents
    clearblob()
    docs = []   
    sorted_uploaded_files = sorted(uploaded_files, key=lambda x: x.name)
    blob_list = container_client.list_blobs()
    existing_blobs = set(blob.name for blob in blob_list)
    for file in uploaded_files:
        file_name = os.path.basename(file.name)
        if file_name not in existing_blobs:
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
            # blob_client = container_client.get_blob_client(folder_name+"/"+file_name)
            blob_client.upload_blob(file)
            existing_blobs.add(file_name)
        else:
           pass

    # Remove old files from the container
    for blob in container_client.list_blobs():
        if blob.name not in existing_blobs:
            container_client.delete_blob(blob.name)


    loader = AzureBlobStorageContainerLoader(conn_str=connection_string, container=container_name)
    docs = loader.load()
    return docs

def getblobdirs():

    blob_items = container_client.list_blobs()
    folders = [blob.name for blob in blob_items if blob.name.endswith("/")]

    return folders
   
def deleteblobdir(foldername):
    blobs = [blob.name for blob in container_client.list_blobs(name_starts_with=foldername)]
     # Delete each blob within the folder
    for blob in blobs:
        container_client.delete_blob(blob)

    print(f"Deleted folder: {foldername}")

def clearblob():

    blob_list = container_client.list_blobs()
    for blob in blob_list:
        container_client.delete_blob(blob)

    is_empty = True if not list(container_client.list_blobs()) else False
    return is_empty
