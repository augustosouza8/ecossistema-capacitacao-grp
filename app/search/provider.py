from abc import ABC, abstractmethod
from typing import TypedDict

from app.catalog.models import CatalogMaterial


class RagResult(TypedDict):
    generated_text: str
    sources: list[CatalogMaterial]


class SearchProvider(ABC):
    @abstractmethod
    def search(self, query: str, top_k: int = 10) -> list[CatalogMaterial]:
        raise NotImplementedError

    @abstractmethod
    def rag_search(self, query: str, top_k: int = 3) -> RagResult:
        raise NotImplementedError
