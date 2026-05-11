from argparse import ArgumentParser
from pathlib import Path
from time import perf_counter
from typing import TYPE_CHECKING, cast

from dotenv import load_dotenv

from app.search.azure_client import build_azure_search_client
from app.search.azure_embeddings import AzureEmbeddingsService
from app.search.azure_openai_client import build_azure_openai_client
from app.search.azure_text_search import AzureTextSearchService

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if TYPE_CHECKING:
    from app.search.azure_embeddings import AzureOpenAIEmbeddingsClient
    from app.search.azure_text_search import SearchExecutor


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    parser = ArgumentParser(
        description="Valida busca hibrida Azure Search + Azure OpenAI embeddings."
    )
    parser.add_argument("query", nargs="?", default="empenho")
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args()

    start = perf_counter()
    embeddings_client = build_azure_openai_client()
    embeddings_service = AzureEmbeddingsService(
        cast("AzureOpenAIEmbeddingsClient", embeddings_client)
    )
    search_client = build_azure_search_client()
    search_service = AzureTextSearchService(
        cast("SearchExecutor", search_client),
        embeddings_service=embeddings_service,
    )
    print("STEP: executing hybrid search...", flush=True)  # noqa: T201
    results = search_service.search_hybrid(args.query, top=args.top)
    elapsed_ms = round((perf_counter() - start) * 1000, 2)

    print("STATUS: OK")  # noqa: T201
    print("CHECK: Azure hybrid search")  # noqa: T201
    print(f"QUERY: {args.query}")  # noqa: T201
    print(f"COUNT: {len(results)}")  # noqa: T201
    print(f"ELAPSED_MS: {elapsed_ms}")  # noqa: T201
    for index, result in enumerate(results, start=1):
        print(  # noqa: T201
            f"{index}. {result.metadata_storage_name} | score={result.search_score}"
        )


if __name__ == "__main__":
    main()
