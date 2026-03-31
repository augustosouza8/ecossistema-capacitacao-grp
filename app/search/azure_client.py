import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient


def build_azure_search_client() -> SearchClient:
    endpoint = _get_required_env("AZURE_SEARCH_ENDPOINT")
    index_name = _get_required_env("AZURE_SEARCH_INDEX_NAME")
    api_key = _get_required_env("AZURE_SEARCH_API_KEY")

    credential = AzureKeyCredential(api_key)
    return SearchClient(
        endpoint=endpoint,
        index_name=index_name,
        credential=credential,
    )


def _get_required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"A variavel de ambiente {name} nao esta configurada.")

    return value
