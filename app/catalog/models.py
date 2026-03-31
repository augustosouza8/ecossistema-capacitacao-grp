from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CatalogMaterial:
    id: int
    type: str
    title: str
    module: str
    theme: str | None = None
    subtheme: str | None = None
    subsubtheme: str | None = None
    keywords: str | None = None
    summary: str | None = None
    source_url: str | None = None
    blob_path: str | None = None
    is_active: bool = True
