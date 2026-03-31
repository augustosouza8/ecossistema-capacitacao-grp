from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class AzureSearchDocument:
    id: str
    metadata_storage_name: str | None
    metadata_storage_path: str | None
    content: str | None
    search_score: float | None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
