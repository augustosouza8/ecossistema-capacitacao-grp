import os

from azure.identity import (
    ClientSecretCredential,
    DefaultAzureCredential,
    get_bearer_token_provider,
)
from openai import AzureOpenAI

REQUIRED_AZURE_OPENAI_ENVS = (
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_VERSION",
    "AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT",
)

AZURE_OPENAI_SCOPE = "https://cognitiveservices.azure.com/.default"


def build_azure_openai_client() -> AzureOpenAI:
    endpoint = _get_required_env("AZURE_OPENAI_ENDPOINT")
    api_version = _get_required_env("AZURE_OPENAI_API_VERSION")
    credential = _build_openai_credential()
    token_provider = get_bearer_token_provider(credential, AZURE_OPENAI_SCOPE)

    return AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        azure_ad_token_provider=token_provider,
    )


def azure_openai_is_configured() -> bool:
    return all(os.environ.get(name, "").strip() for name in REQUIRED_AZURE_OPENAI_ENVS)


def get_embeddings_deployment() -> str:
    return _get_required_env("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT")


def _build_openai_credential() -> ClientSecretCredential | DefaultAzureCredential:
    tenant_id = os.environ.get("AZURE_TENANT_ID", "").strip()
    client_id = os.environ.get("AZURE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("AZURE_CLIENT_SECRET", "").strip()

    if tenant_id and client_id and client_secret:
        return ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )

    return DefaultAzureCredential(
        exclude_environment_credential=True,
        exclude_interactive_browser_credential=False,
    )


def _get_required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"A variavel de ambiente {name} nao esta configurada.")

    return value
