from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest
from azure.search.documents.models import VectorizedQuery, VectorQuery
from flask import Flask

from app.catalog.excel_repository import ExcelCatalogRepository
from app.search.azure_embeddings import AzureEmbeddingsService
from app.search.azure_models import AzureSearchDocument
from app.search.azure_text_search import AzureTextSearchService
from app.search.local_provider import LocalCatalogSearchProvider

if TYPE_CHECKING:
    from app.search.azure_embeddings import AzureOpenAIEmbeddingsClient


class StubAzureSearchClient:
    def search(
        self,
        *,
        search_text: str,
        top: int,
        select: list[str],
        vector_queries: list[VectorQuery] | None = None,
    ) -> list[dict[str, object]]:
        assert search_text == "empenho"
        assert top == 3
        assert select == [
            "id",
            "metadata_storage_name",
            "metadata_storage_path",
            "content",
        ]
        assert vector_queries is None
        return [
            {
                "id": "abc-123",
                "metadata_storage_name": "POP_101__empenho-inclusao-ordinario.docx",
                "metadata_storage_path": "https://storage/path.docx",
                "content": "Passo a passo de empenho ordinario.",
                "@search.score": 2.75,
            }
        ]


class StubHybridAzureSearchClient:
    def search(
        self,
        *,
        search_text: str,
        top: int,
        select: list[str],
        vector_queries: list[VectorQuery] | None = None,
    ) -> list[dict[str, object]]:
        assert search_text == "empenho"
        assert top == 4
        assert select == [
            "id",
            "metadata_storage_name",
            "metadata_storage_path",
            "content",
        ]
        assert vector_queries is not None
        assert len(vector_queries) == 1
        query = vector_queries[0]
        assert isinstance(query, VectorizedQuery)
        assert query.fields == "content_vector"
        assert query.k_nearest_neighbors == 4
        assert query.vector == [0.1, 0.2, 0.3]
        return [
            {
                "id": "hybrid-123",
                "metadata_storage_name": "POP_105__empenho-reforco.docx",
                "metadata_storage_path": "https://storage/hybrid.docx",
                "content": "Instrucoes para reforco de empenho.",
                "@search.score": 3.15,
            }
        ]


class StubEmbeddingResponseItem:
    def __init__(self) -> None:
        self.embedding = [0.1, 0.2, 0.3]


class StubEmbeddingResponse:
    def __init__(self) -> None:
        self.data = [StubEmbeddingResponseItem()]


class StubEmbeddingsCreator:
    def create(self, **kwargs: object) -> StubEmbeddingResponse:
        assert kwargs["model"] == "text-embedding-3-small"
        assert kwargs["input"] == "empenho"

        return StubEmbeddingResponse()


class StubAzureOpenAIClient:
    def __init__(self) -> None:
        self._embeddings = StubEmbeddingsCreator()

    @property
    def embeddings(self) -> StubEmbeddingsCreator:
        return self._embeddings


def test_search_contract(app: Flask) -> None:
    with app.app_context():
        repository = ExcelCatalogRepository(Path(app.config["CATALOG_XLSX_PATH"]))
        provider = LocalCatalogSearchProvider(repository)

        results = provider.search("guia")
        assert isinstance(results, list)
        assert len(results) == 1
        assert all(hasattr(r, "id") and hasattr(r, "title") for r in results)

        rag_res = provider.rag_search("empenho")
        assert isinstance(rag_res, dict)
        assert "generated_text" in rag_res
        assert "sources" in rag_res
        assert len(rag_res["sources"]) == 1
        assert "Empenho guia" in rag_res["generated_text"]


def test_azure_text_search_mapping() -> None:
    service = AzureTextSearchService(StubAzureSearchClient())

    results = service.search_text("empenho", top=3)

    assert results == [
        AzureSearchDocument(
            id="abc-123",
            metadata_storage_name="POP_101__empenho-inclusao-ordinario.docx",
            metadata_storage_path="https://storage/path.docx",
            content="Passo a passo de empenho ordinario.",
            search_score=2.75,
        )
    ]


def test_azure_hybrid_search_mapping(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT", "text-embedding-3-small")

    embeddings_service = AzureEmbeddingsService(
        cast("AzureOpenAIEmbeddingsClient", StubAzureOpenAIClient())
    )
    service = AzureTextSearchService(
        StubHybridAzureSearchClient(),
        embeddings_service=embeddings_service,
    )

    results = service.search_hybrid("empenho", top=4)

    assert results == [
        AzureSearchDocument(
            id="hybrid-123",
            metadata_storage_name="POP_105__empenho-reforco.docx",
            metadata_storage_path="https://storage/hybrid.docx",
            content="Instrucoes para reforco de empenho.",
            search_score=3.15,
        )
    ]
