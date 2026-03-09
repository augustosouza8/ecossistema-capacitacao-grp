from abc import ABC, abstractmethod
from typing import Any


class SearchProvider(ABC):
    @abstractmethod
    def search(self, query: str, top_k: int = 10) -> list[Any]:
        pass

    @abstractmethod
    def rag_search(self, query: str, top_k: int = 3) -> dict[str, Any]:
        pass
