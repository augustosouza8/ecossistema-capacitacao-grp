import os
from datetime import UTC, datetime, timedelta

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobSasPermissions, BlobServiceClient, generate_blob_sas


def get_blob_sas_url(blob_path: str) -> str:
    """
    Gera uma URL SAS segura para acesso temporário (15 minutos) a um arquivo .docx
    no Azure Blob Storage, utilizando Managed Identity.
    """
    account_url = os.environ.get("AZURE_STORAGE_ACCOUNT_URL")
    if not account_url:
        raise ValueError("A variável AZURE_STORAGE_ACCOUNT_URL não está configurada.")

    container_name = "materials"

    # Em produção, usa Managed Identity. Localmente, usa seu login do VSCode/CLI.
    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(account_url, credential=credential)

    # Adquire uma chave de delegação do usuário (User Delegation Key)
    # Exige que a Managed Identity tenha a role "Storage Blob Delegator" no IAM.
    key_start_time = datetime.now(UTC)
    key_expiry_time = key_start_time + timedelta(hours=1)
    udk = blob_service_client.get_user_delegation_key(
        key_start_time=key_start_time,
        key_expiry_time=key_expiry_time,
    )

    sas_token = generate_blob_sas(
        account_name=str(blob_service_client.account_name),
        container_name=container_name,
        blob_name=blob_path,
        user_delegation_key=udk,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.now(UTC) + timedelta(minutes=15),
    )

    return f"{account_url}/{container_name}/{blob_path}?{sas_token}"
