from collections.abc import Iterable, Mapping, Sequence
from typing import Protocol

from azure.search.documents.models import VectorizedQuery, VectorQuery

from app.search.azure_embeddings import AzureEmbeddingsService
from app.search.azure_models import AzureSearchDocument

SEARCH_FIELDS: Sequence[str] = (
    "id",
    "metadata_storage_name",
    "metadata_storage_path",
    "content",
)


class SearchExecutor(Protocol):
    def search(
        self,
        *,
        search_text: str,
        top: int,
        select: list[str],
        vector_queries: list[VectorQuery] | None = None,
    ) -> Iterable[Mapping[str, object]]: ...


class AzureTextSearchService:
    def __init__(
        self,
        client: SearchExecutor,
        embeddings_service: AzureEmbeddingsService | None = None,
    ) -> None:
        self._client = client
        self._embeddings_service = embeddings_service

    def search_text(self, query: str, top: int = 5) -> list[AzureSearchDocument]:
        normalized_query = query.strip()
        if not normalized_query:
            return []

        safe_top = min(max(top, 1), 50)
        results: Iterable[Mapping[str, object]] = self._client.search(
            search_text=normalized_query,
            top=safe_top,
            select=list(SEARCH_FIELDS),
        )
        return [self._map_result(result) for result in results]

    def search_hybrid(self, query: str, top: int = 10) -> list[AzureSearchDocument]:
        normalized_query = query.strip()
        if not normalized_query:
            return []

        if self._embeddings_service is None:
            raise RuntimeError(
                "A busca hibrida nao esta configurada no ambiente atual."
            )

        safe_top = min(max(top, 1), 50)
        embedding = self._embeddings_service.embed_query(normalized_query)
        vector_query = VectorizedQuery(
            vector=embedding,
            fields="content_vector",
            k_nearest_neighbors=safe_top,
        )
        results: Iterable[Mapping[str, object]] = self._client.search(
            search_text=normalized_query,
            top=safe_top,
            select=list(SEARCH_FIELDS),
            vector_queries=[vector_query],
        )
        return [self._map_result(result) for result in results]

    def _map_result(self, result: Mapping[str, object]) -> AzureSearchDocument:
        document = dict(result)
        return AzureSearchDocument(
            id=self._read_required_str(document, "id"),
            metadata_storage_name=self._read_optional_str(
                document,
                "metadata_storage_name",
            ),
            metadata_storage_path=self._read_optional_str(
                document,
                "metadata_storage_path",
            ),
            content=self._read_optional_str(document, "content"),
            search_score=self._read_optional_float(document, "@search.score"),
        )

    @staticmethod
    def _read_required_str(document: dict[str, object], key: str) -> str:
        value = document.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Resultado do Azure Search sem campo obrigatorio: {key}")

        return value

    @staticmethod
    def _read_optional_str(document: dict[str, object], key: str) -> str | None:
        value = document.get(key)
        if value is None:
            return None
        if isinstance(value, str):
            return value

        raise ValueError(f"Campo {key} retornou com tipo invalido no Azure Search")

    @staticmethod
    def _read_optional_float(document: dict[str, object], key: str) -> float | None:
        value = document.get(key)
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)

        raise ValueError(f"Campo {key} retornou com tipo invalido no Azure Search")
