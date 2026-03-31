import os
from argparse import ArgumentParser
from pathlib import Path
from time import perf_counter

from dotenv import load_dotenv

from app.search.azure_openai_client import build_azure_openai_client

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    parser = ArgumentParser(
        description="Valida chamada ao deployment de chat no Azure OpenAI."
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        default="Responda apenas com OK.",
    )
    args = parser.parse_args()

    deployment = _get_chat_deployment()
    client = build_azure_openai_client()

    print("STEP: requesting chat response from Azure OpenAI...", flush=True)  # noqa: T201
    start = perf_counter()
    response = client.responses.create(
        model=deployment,
        input=args.prompt,
        max_output_tokens=50,
    )
    elapsed_ms = round((perf_counter() - start) * 1000, 2)

    print("STATUS: OK")  # noqa: T201
    print("CHECK: Azure OpenAI chat")  # noqa: T201
    print(f"DEPLOYMENT: {deployment}")  # noqa: T201
    print(f"PROMPT: {args.prompt}")  # noqa: T201
    print(f"ELAPSED_MS: {elapsed_ms}")  # noqa: T201
    print(f"RESPONSE_ID: {response.id}")  # noqa: T201
    print(f"OUTPUT_TEXT: {response.output_text}")  # noqa: T201


def _get_chat_deployment() -> str:
    deployment = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT", "").strip()
    if not deployment:
        raise ValueError(
            "A variavel de ambiente AZURE_OPENAI_CHAT_DEPLOYMENT nao esta configurada."
        )

    return deployment


if __name__ == "__main__":
    main()
