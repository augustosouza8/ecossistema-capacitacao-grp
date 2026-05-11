import os
import socket
from argparse import ArgumentParser
from pathlib import Path
from time import perf_counter
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_ENDPOINTS = {
    "entra_openid": "https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration",
    "azure_openai": "AZURE_OPENAI_ENDPOINT",
    "azure_search": "AZURE_SEARCH_ENDPOINT",
}


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    parser = ArgumentParser(
        description="Valida DNS e conectividade HTTPS basica para os endpoints Azure."
    )
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()

    for label, endpoint_or_env in DEFAULT_ENDPOINTS.items():
        url = _resolve_url(endpoint_or_env)
        print(f"CHECK: {label}")  # noqa: T201
        print(f"URL: {url}")  # noqa: T201
        _check_dns(url)
        _check_https(url, timeout=args.timeout)
        print("---")  # noqa: T201


def _resolve_url(endpoint_or_env: str) -> str:
    if endpoint_or_env.startswith("http"):
        return endpoint_or_env

    value = os.environ.get(endpoint_or_env, "").strip()
    if not value:
        raise ValueError(
            f"A variavel de ambiente {endpoint_or_env} nao esta configurada."
        )

    return value


def _check_dns(url: str) -> None:
    hostname = urlparse(url).hostname
    if not hostname:
        raise ValueError(f"Nao foi possivel identificar o host da URL: {url}")

    start = perf_counter()
    addresses = socket.getaddrinfo(hostname, 443, proto=socket.IPPROTO_TCP)
    elapsed_ms = round((perf_counter() - start) * 1000, 2)
    unique_ips = sorted({str(item[4][0]) for item in addresses})
    print(f"DNS_OK: {hostname}")  # noqa: T201
    print(f"DNS_IPS: {', '.join(unique_ips[:5])}")  # noqa: T201
    print(f"DNS_ELAPSED_MS: {elapsed_ms}")  # noqa: T201


def _check_https(url: str, *, timeout: float) -> None:
    start = perf_counter()
    response = requests.get(url, timeout=timeout, allow_redirects=True)
    elapsed_ms = round((perf_counter() - start) * 1000, 2)
    print(f"HTTPS_STATUS: {response.status_code}")  # noqa: T201
    print(f"HTTPS_ELAPSED_MS: {elapsed_ms}")  # noqa: T201
    print(f"SERVER: {response.headers.get('server', '<none>')}")  # noqa: T201


if __name__ == "__main__":
    main()
