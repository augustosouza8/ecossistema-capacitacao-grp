from argparse import ArgumentParser
from pathlib import Path
from time import perf_counter
from typing import TYPE_CHECKING, cast

from dotenv import load_dotenv

from app.search.azure_embeddings import AzureEmbeddingsService
from app.search.azure_openai_client import (
    build_azure_openai_client,
    get_embeddings_deployment,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if TYPE_CHECKING:
    from app.search.azure_embeddings import AzureOpenAIEmbeddingsClient


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    parser = ArgumentParser(description="Valida geracao de embeddings no Azure OpenAI.")
    parser.add_argument("query", nargs="?", default="empenho")
    args = parser.parse_args()

    start = perf_counter()
    client = build_azure_openai_client()
    service = AzureEmbeddingsService(cast("AzureOpenAIEmbeddingsClient", client))
    print("STEP: requesting embedding from Azure OpenAI...", flush=True)  # noqa: T201
    embedding = service.embed_query(args.query)
    elapsed_ms = round((perf_counter() - start) * 1000, 2)

    print("STATUS: OK")  # noqa: T201
    print("CHECK: Azure OpenAI embeddings")  # noqa: T201
    print(f"QUERY: {args.query}")  # noqa: T201
    print(f"DEPLOYMENT: {get_embeddings_deployment()}")  # noqa: T201
    print(f"DIMENSIONS: {len(embedding)}")  # noqa: T201
    print(f"ELAPSED_MS: {elapsed_ms}")  # noqa: T201
    print(f"VECTOR_PREVIEW: {embedding[:5]}")  # noqa: T201


if __name__ == "__main__":
    main()
