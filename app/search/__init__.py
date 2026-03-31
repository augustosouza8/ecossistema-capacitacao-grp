from app.search.azure_client import build_azure_search_client
from app.search.azure_embeddings import AzureEmbeddingsService
from app.search.azure_models import AzureSearchDocument
from app.search.azure_openai_client import (
    azure_openai_is_configured,
    build_azure_openai_client,
    get_embeddings_deployment,
)
from app.search.azure_text_search import AzureTextSearchService
from app.search.local_provider import LocalCatalogSearchProvider
from app.search.provider import RagResult, SearchProvider
