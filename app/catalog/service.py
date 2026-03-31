from dataclasses import dataclass
from math import ceil

from app.catalog.models import CatalogMaterial
from app.catalog.repository import CatalogRepository

CatalogTree = dict[str, dict[str, dict[str, dict[str, list[CatalogMaterial]]]]]


@dataclass(frozen=True, slots=True)
class CatalogPage:
    items: list[CatalogMaterial]
    total: int
    page: int
    per_page: int
    total_pages: int


class CatalogService:
    def __init__(self, repository: CatalogRepository) -> None:
        self._repository = repository

    @property
    def repository(self) -> CatalogRepository:
        return self._repository

    def get_all_materials_linear(
        self,
        query: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> CatalogPage:
        normalized_query = (query or "").strip().casefold()
        materials = self._repository.list_materials()

        if normalized_query:
            materials = [
                material
                for material in materials
                if normalized_query in material.title.casefold()
            ]

        safe_page = max(page, 1)
        safe_per_page = max(per_page, 1)
        total = len(materials)
        total_pages = max(ceil(total / safe_per_page), 1)
        clamped_page = min(safe_page, total_pages)
        start_index = (clamped_page - 1) * safe_per_page
        end_index = start_index + safe_per_page

        return CatalogPage(
            items=materials[start_index:end_index],
            total=total,
            page=clamped_page,
            per_page=safe_per_page,
            total_pages=total_pages,
        )

    def get_materials_tree(self) -> CatalogTree:
        tree: CatalogTree = {}
        for material in self._repository.list_materials():
            module_bucket = tree.setdefault(material.module, {})
            theme_bucket = module_bucket.setdefault(material.theme or "", {})
            subtheme_bucket = theme_bucket.setdefault(material.subtheme or "", {})
            materials_bucket = subtheme_bucket.setdefault(
                material.subsubtheme or "", []
            )
            materials_bucket.append(material)

        return tree
