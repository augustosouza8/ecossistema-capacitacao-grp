import os
from pathlib import Path
from typing import TYPE_CHECKING, cast

from dotenv import load_dotenv
from flask import Flask

from app.catalog.excel_repository import ExcelCatalogRepository
from app.catalog.service import CatalogService
from app.routes.ui import ui_bp
from app.search.azure_client import build_azure_search_client
from app.search.azure_embeddings import AzureEmbeddingsService
from app.search.azure_openai_client import (
    azure_openai_is_configured,
    build_azure_openai_client,
)
from app.search.azure_text_search import AzureTextSearchService
from app.search.local_provider import LocalCatalogSearchProvider
from app.search.provider import SearchProvider

if TYPE_CHECKING:
    from app.search.azure_embeddings import AzureOpenAIEmbeddingsClient
    from app.search.azure_text_search import SearchExecutor

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev_secret_key")
    catalog_path = _resolve_catalog_path(
        os.environ.get("CATALOG_XLSX_PATH", "data/imports/materials.xlsx")
    )
    app.config["CATALOG_XLSX_PATH"] = str(catalog_path)

    catalog_repository = ExcelCatalogRepository(catalog_path)
    catalog_service = CatalogService(catalog_repository)
    azure_text_search_service = _build_azure_text_search_service()
    search_provider = _build_search_provider(
        os.environ.get("SEARCH_PROVIDER", "local"),
        catalog_repository,
    )

    app.extensions["catalog_repository"] = catalog_repository
    app.extensions["catalog_service"] = catalog_service
    app.extensions["azure_text_search_service"] = azure_text_search_service
    app.extensions["search_provider"] = search_provider

    app.register_blueprint(ui_bp)

    return app


def _resolve_catalog_path(raw_path: str) -> Path:
    catalog_path = Path(raw_path)
    if not catalog_path.is_absolute():
        catalog_path = Path(__file__).parent.parent / catalog_path

    resolved_path = catalog_path.resolve()
    if not resolved_path.exists():
        raise FileNotFoundError(f"Catalogo Excel nao encontrado em: {resolved_path}")

    return resolved_path


def _build_search_provider(
    provider_name: str,
    catalog_repository: ExcelCatalogRepository,
) -> SearchProvider:
    normalized_name = provider_name.strip().casefold()
    if normalized_name == "local":
        return LocalCatalogSearchProvider(catalog_repository)

    raise ValueError(f"SEARCH_PROVIDER nao suportado nesta fase: {provider_name}")


def _build_azure_text_search_service() -> AzureTextSearchService:
    client = build_azure_search_client()
    embeddings_service = _build_embeddings_service()
    return AzureTextSearchService(
        cast("SearchExecutor", client),
        embeddings_service=embeddings_service,
    )


def _build_embeddings_service() -> AzureEmbeddingsService | None:
    if not azure_openai_is_configured():
        return None

    client = build_azure_openai_client()
    return AzureEmbeddingsService(cast("AzureOpenAIEmbeddingsClient", client))
