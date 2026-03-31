from collections.abc import Sequence
from typing import Protocol

from app.search.azure_openai_client import get_embeddings_deployment


class EmbeddingsResponseDataItem(Protocol):
    embedding: Sequence[float]


class EmbeddingsResponse(Protocol):
    data: Sequence[EmbeddingsResponseDataItem]


class EmbeddingsCreator(Protocol):
    def create(self, **kwargs: object) -> EmbeddingsResponse: ...


class AzureOpenAIEmbeddingsClient(Protocol):
    @property
    def embeddings(self) -> EmbeddingsCreator: ...


class AzureEmbeddingsService:
    def __init__(self, client: AzureOpenAIEmbeddingsClient) -> None:
        self._client = client
        self._deployment = get_embeddings_deployment()

    def embed_query(self, query: str) -> list[float]:
        normalized_query = query.strip()
        if not normalized_query:
            return []

        response = self._client.embeddings.create(
            model=self._deployment, input=normalized_query
        )
        if not response.data:
            raise ValueError("O Azure OpenAI nao retornou embedding para a consulta.")

        embedding = list(response.data[0].embedding)
        if not embedding:
            raise ValueError("O embedding retornado pelo Azure OpenAI esta vazio.")

        return embedding
