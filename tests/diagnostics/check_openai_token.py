from argparse import ArgumentParser
from pathlib import Path
from time import perf_counter

from azure.core.credentials import AccessToken
from dotenv import load_dotenv

from app.search.azure_openai_client import AZURE_OPENAI_SCOPE, _build_openai_credential

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    parser = ArgumentParser(
        description="Valida obtencao de token Entra ID para Azure OpenAI."
    )
    parser.parse_args()

    start = perf_counter()
    credential = _build_openai_credential()
    print("STEP: requesting Entra ID token...", flush=True)  # noqa: T201
    token = credential.get_token(AZURE_OPENAI_SCOPE)
    elapsed_ms = round((perf_counter() - start) * 1000, 2)

    _print_success(token, elapsed_ms)


def _print_success(token: AccessToken, elapsed_ms: float) -> None:
    print("STATUS: OK")  # noqa: T201
    print("CHECK: Azure OpenAI token")  # noqa: T201
    print(f"SCOPE: {AZURE_OPENAI_SCOPE}")  # noqa: T201
    print(f"ELAPSED_MS: {elapsed_ms}")  # noqa: T201
    print(f"TOKEN_PREFIX: {token.token[:20]}...")  # noqa: T201
    print(f"EXPIRES_ON: {token.expires_on}")  # noqa: T201


if __name__ == "__main__":
    main()
