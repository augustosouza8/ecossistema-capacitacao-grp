from abc import ABC, abstractmethod
from collections.abc import Mapping

from app.catalog.models import CatalogMaterial


class CatalogRepository(ABC):
    @abstractmethod
    def list_materials(self) -> list[CatalogMaterial]:
        raise NotImplementedError

    @abstractmethod
    def get_metadata(self) -> Mapping[str, object]:
        raise NotImplementedError
