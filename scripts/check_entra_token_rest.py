import os
from argparse import ArgumentParser
from pathlib import Path
from time import perf_counter

import requests
from dotenv import load_dotenv

from app.search.azure_openai_client import AZURE_OPENAI_SCOPE

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    parser = ArgumentParser(
        description="Valida a obtencao de token Entra ID via REST e client credentials."
    )
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args()

    tenant_id = _get_required_env("AZURE_TENANT_ID")
    client_id = _get_required_env("AZURE_CLIENT_ID")
    client_secret = _get_required_env("AZURE_CLIENT_SECRET")
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

    print("STEP: requesting token via REST...", flush=True)  # noqa: T201
    start = perf_counter()
    response = requests.post(
        token_url,
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": AZURE_OPENAI_SCOPE,
        },
        timeout=args.timeout,
    )
    elapsed_ms = round((perf_counter() - start) * 1000, 2)

    print(f"HTTP_STATUS: {response.status_code}")  # noqa: T201
    print(f"ELAPSED_MS: {elapsed_ms}")  # noqa: T201
    payload = response.json()
    if response.ok:
        access_token = str(payload["access_token"])
        print("STATUS: OK")  # noqa: T201
        print(f"TOKEN_PREFIX: {access_token[:20]}...")  # noqa: T201
        print(f"EXPIRES_IN: {payload.get('expires_in')}")  # noqa: T201
        return

    print("STATUS: ERROR")  # noqa: T201
    print(f"ERROR: {payload.get('error')}")  # noqa: T201
    print(f"ERROR_DESCRIPTION: {payload.get('error_description')}")  # noqa: T201


def _get_required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"A variavel de ambiente {name} nao esta configurada.")

    return value


if __name__ == "__main__":
    main()
