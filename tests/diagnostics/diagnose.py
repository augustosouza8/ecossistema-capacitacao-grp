"""
Script de diagnóstico completo para validar configuração e conectividade
com serviços Azure (OpenAI, AI Search) da aplicação Ecossistema GRP.

Uso:
    python scripts/diagnose.py [--skip-search]
    
Opções:
    --skip-search: Pula testes de Azure AI Search (opcional)
"""

import os
import socket
from argparse import ArgumentParser
from pathlib import Path
from time import perf_counter
from typing import Any
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Variáveis obrigatórias para OpenAI
REQUIRED_OPENAI_ENVS = {
    "AZURE_TENANT_ID": "ID do tenant Azure Entra ID",
    "AZURE_CLIENT_ID": "ID da aplicação/Service Principal",
    "AZURE_CLIENT_SECRET": "Secret da aplicação",
    "AZURE_OPENAI_ENDPOINT": "URL do recurso Azure OpenAI (ex: https://...openai.azure.com/)",
    "AZURE_OPENAI_API_VERSION": "Versão da API (ex: 2025-01-01-preview)",
    "AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT": "Nome do deployment de embeddings",
    "AZURE_OPENAI_CHAT_DEPLOYMENT": "Nome do deployment de chat",
}

# Variáveis opcionais para AI Search
OPTIONAL_SEARCH_ENVS = {
    "AZURE_SEARCH_ENDPOINT": "URL do recurso Azure AI Search",
    "AZURE_SEARCH_INDEX_NAME": "Nome do índice de busca",
    "AZURE_SEARCH_API_KEY": "Chave de API do AI Search",
}

AZURE_OPENAI_SCOPE = "https://cognitiveservices.azure.com/.default"


class DiagnosticResult:
    """Holder para resultados de cada etapa do diagnóstico."""
    
    def __init__(self) -> None:
        self.checks: dict[str, dict[str, Any]] = {}
        self.passed: int = 0
        self.failed: int = 0
        self.skipped: int = 0

    def add_pass(self, check_name: str, details: dict[str, str]) -> None:
        """Registra um check bem-sucedido."""
        self.checks[check_name] = {"status": "✓ PASS", **details}
        self.passed += 1

    def add_fail(self, check_name: str, error: str, details: dict[str, str] | None = None) -> None:
        """Registra um check que falhou."""
        self.checks[check_name] = {
            "status": "✗ FAIL",
            "error": error,
            **(details or {}),
        }
        self.failed += 1

    def add_skip(self, check_name: str, reason: str) -> None:
        """Registra um check pulado."""
        self.checks[check_name] = {"status": "⊘ SKIP", "reason": reason}
        self.skipped += 1

    def print_report(self) -> None:
        """Imprime relatório formatado de todos os checks."""
        print("\n" + "=" * 80)  # noqa: T201
        print("DIAGNÓSTICO COMPLETO - ECOSSISTEMA GRP")  # noqa: T201
        print("=" * 80)  # noqa: T201

        for check_name, details in self.checks.items():
            status = details.pop("status")
            print(f"\n[{status}] {check_name}")  # noqa: T201
            for key, value in details.items():
                print(f"    {key}: {value}")  # noqa: T201

        print("\n" + "-" * 80)  # noqa: T201
        print(f"RESUMO: {self.passed} passed, {self.failed} failed, {self.skipped} skipped")  # noqa: T201
        print("-" * 80)  # noqa: T201

        if self.failed > 0:
            self._print_remediation()

    def _print_remediation(self) -> None:
        """Imprime sugestões de correção baseadas nos erros encontrados."""
        print("\nPRÓXIMOS PASSOS:")  # noqa: T201

        for check_name, details in self.checks.items():
            if details.get("status") == "✗ FAIL":
                error = details.get("error", "")

                if "403" in error and "Virtual Network" in error:
                    print("  1. FIREWALL/VNET BLOQUEANDO ACESSO:")  # noqa: T201
                    print("     - Seu IP não está autorizado no firewall do Azure OpenAI")  # noqa: T201
                    print("     - Contate o admin Azure/SEF-MG para:")  # noqa: T201
                    print("       * Liberar seu IP público no firewall do recurso")  # noqa: T201
                    print("       * Ou confirmar VPN corporativa necessária")  # noqa: T201

                elif "não está configurada" in error or "INVALID" in error:
                    print("  2. VARIÁVEIS DE AMBIENTE INVÁLIDAS:")  # noqa: T201
                    print(f"     - Verifique o arquivo .env (cópia do .env.example)")  # noqa: T201
                    print(f"     - Problema em: {check_name}")  # noqa: T201

                elif "DNS" in error or "resolve" in error.upper():
                    print("  3. PROBLEMA DE REDE/DNS:")  # noqa: T201
                    print("     - Verifique conexão com a internet")  # noqa: T201
                    print("     - URLs dos endpoints Azure podem estar incorretas")  # noqa: T201

                elif "timeout" in error.lower():
                    print("  4. TIMEOUT NA CONEXÃO:")  # noqa: T201
                    print("     - Firewall corporativo pode estar bloqueando acesso")  # noqa: T201
                    print("     - Tente com timeout maior ou desabilite proxy")  # noqa: T201


def main() -> None:
    """Executa diagnóstico completo."""
    load_dotenv(PROJECT_ROOT / ".env")
    parser = ArgumentParser(
        description="Diagnóstico completo de configuração e conectividade Azure."
    )
    parser.add_argument(
        "--skip-search",
        action="store_true",
        help="Pula testes de Azure AI Search",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Timeout para requisições HTTP (padrão: 10s)",
    )
    args = parser.parse_args()

    result = DiagnosticResult()

    # Fase 1: Validar .env
    _check_env_vars(result)

    # Fase 2: Validar autenticação Entra ID
    _check_entra_token(result)

    # Fase 3: Validar conectividade de rede
    _check_network_endpoints(result, timeout=args.timeout)

    # Fase 4: Testar Azure OpenAI
    _check_azure_openai_embeddings(result)
    _check_azure_openai_chat(result)

    # Fase 5: Testar Azure AI Search (opcional)
    if not args.skip_search:
        _check_azure_search(result, timeout=args.timeout)

    # Imprimir relatório final
    result.print_report()

    # Retornar código de saída apropriado
    exit(0 if result.failed == 0 else 1)


def _check_env_vars(result: DiagnosticResult) -> None:
    """Valida presença de variáveis de ambiente obrigatórias."""
    missing = []
    invalid = []

    for env_var, description in REQUIRED_OPENAI_ENVS.items():
        value = os.environ.get(env_var, "").strip()
        if not value:
            missing.append(f"{env_var}: {description}")
        elif len(value) < 3:
            invalid.append(f"{env_var}: valor muito curto")

    if missing or invalid:
        error_msg = "Variáveis obrigatórias não configuradas:\n" + "\n".join(missing + invalid)
        result.add_fail("Config: Variáveis de Ambiente", error_msg)
    else:
        result.add_pass(
            "Config: Variáveis de Ambiente",
            {
                "openai_vars": "7 de 7 configuradas",
                "arquivo": ".env OK",
            },
        )


def _check_entra_token(result: DiagnosticResult) -> None:
    """Valida obtenção de token Entra ID."""
    try:
        from app.search.azure_openai_client import (
            AZURE_OPENAI_SCOPE,
            _build_openai_credential,
        )

        start = perf_counter()
        credential = _build_openai_credential()
        token = credential.get_token(AZURE_OPENAI_SCOPE)
        elapsed_ms = round((perf_counter() - start) * 1000, 2)

        result.add_pass(
            "Auth: Token Entra ID",
            {
                "token_prefix": token.token[:20] + "...",
                "expires_on": str(token.expires_on),
                "elapsed_ms": str(elapsed_ms),
            },
        )
    except ValueError as e:
        result.add_fail(
            "Auth: Token Entra ID",
            f"Credenciais inválidas: {str(e)}",
            {"sugestão": "Verifique AZURE_TENANT_ID, CLIENT_ID e CLIENT_SECRET"},
        )
    except Exception as e:
        result.add_fail(
            "Auth: Token Entra ID",
            f"Erro ao obter token: {type(e).__name__}: {str(e)}",
        )


def _check_network_endpoints(result: DiagnosticResult, *, timeout: float) -> None:
    """Valida conectividade de rede aos endpoints Azure."""
    endpoints = {
        "Azure OpenAI": os.environ.get("AZURE_OPENAI_ENDPOINT", "").strip(),
        "Azure Search": os.environ.get("AZURE_SEARCH_ENDPOINT", "").strip(),
    }

    for name, url in endpoints.items():
        if not url:
            result.add_skip(f"Network: {name}", f"Endpoint não configurado")
            continue

        try:
            # Check DNS
            hostname = urlparse(url).hostname
            if not hostname:
                result.add_fail(
                    f"Network: {name}",
                    f"URL inválida: {url}",
                )
                continue

            start_dns = perf_counter()
            socket.getaddrinfo(hostname, 443, proto=socket.IPPROTO_TCP)
            dns_ms = round((perf_counter() - start_dns) * 1000, 2)

            # Check HTTPS
            start_https = perf_counter()
            response = requests.get(url, timeout=timeout, allow_redirects=True)
            https_ms = round((perf_counter() - start_https) * 1000, 2)

            result.add_pass(
                f"Network: {name}",
                {
                    "hostname": hostname,
                    "dns_ms": str(dns_ms),
                    "https_status": str(response.status_code),
                    "https_ms": str(https_ms),
                },
            )
        except socket.gaierror as e:
            result.add_fail(
                f"Network: {name}",
                f"Erro de DNS: {str(e)}",
                {"hostname": urlparse(url).hostname or "?"},
            )
        except requests.Timeout:
            result.add_fail(
                f"Network: {name}",
                f"Timeout na conexão HTTPS (>{timeout}s)",
                {"url": url},
            )
        except requests.RequestException as e:
            result.add_fail(
                f"Network: {name}",
                f"Erro na requisição HTTP: {str(e)}",
                {"url": url},
            )


def _check_azure_openai_embeddings(result: DiagnosticResult) -> None:
    """Testa geração de embeddings no Azure OpenAI."""
    try:
        from app.search.azure_embeddings import AzureEmbeddingsService
        from app.search.azure_openai_client import build_azure_openai_client

        start = perf_counter()
        client = build_azure_openai_client()
        service = AzureEmbeddingsService(client)
        embedding = service.embed_query("teste")
        elapsed_ms = round((perf_counter() - start) * 1000, 2)

        result.add_pass(
            "Azure OpenAI: Embeddings",
            {
                "deployment": os.environ.get("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT", "?"),
                "dimensões": str(len(embedding)),
                "elapsed_ms": str(elapsed_ms),
            },
        )
    except ValueError as e:
        error_msg = str(e)
        if "Virtual Network" in error_msg or "403" in error_msg:
            result.add_fail(
                "Azure OpenAI: Embeddings",
                error_msg,
                {"causa": "Firewall/VNET bloqueando acesso"},
            )
        else:
            result.add_fail(
                "Azure OpenAI: Embeddings",
                error_msg,
            )
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        result.add_fail(
            "Azure OpenAI: Embeddings",
            error_msg,
        )


def _check_azure_openai_chat(result: DiagnosticResult) -> None:
    """Testa chamada de chat no Azure OpenAI."""
    try:
        from app.search.azure_openai_client import build_azure_openai_client

        deployment = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT", "").strip()
        if not deployment:
            result.add_fail(
                "Azure OpenAI: Chat",
                "AZURE_OPENAI_CHAT_DEPLOYMENT não está configurada",
            )
            return

        start = perf_counter()
        client = build_azure_openai_client()
        
        # Tenta chamada de chat simples
        response = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": "Responda apenas com OK."}],
            max_tokens=10,
        )
        elapsed_ms = round((perf_counter() - start) * 1000, 2)

        result.add_pass(
            "Azure OpenAI: Chat",
            {
                "deployment": deployment,
                "response_id": response.id[:16] + "...",
                "elapsed_ms": str(elapsed_ms),
            },
        )
    except ValueError as e:
        error_msg = str(e)
        if "Virtual Network" in error_msg or "403" in error_msg:
            result.add_fail(
                "Azure OpenAI: Chat",
                error_msg,
                {"causa": "Firewall/VNET bloqueando acesso"},
            )
        else:
            result.add_fail(
                "Azure OpenAI: Chat",
                error_msg,
            )
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        result.add_fail(
            "Azure OpenAI: Chat",
            error_msg,
        )


def _check_azure_search(result: DiagnosticResult, *, timeout: float) -> None:
    """Testa conectividade com Azure AI Search."""
    endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT", "").strip()
    api_key = os.environ.get("AZURE_SEARCH_API_KEY", "").strip()
    index_name = os.environ.get("AZURE_SEARCH_INDEX_NAME", "").strip()

    if not (endpoint and api_key and index_name):
        result.add_skip(
            "Azure AI Search",
            "Variáveis não configuradas (SEARCH_PROVIDER=local)",
        )
        return

    try:
        start = perf_counter()
        url = f"{endpoint}/indexes('{index_name}')?api-version=2023-11-01"
        headers = {"api-key": api_key}
        response = requests.get(url, headers=headers, timeout=timeout)
        elapsed_ms = round((perf_counter() - start) * 1000, 2)

        if response.status_code == 200:
            result.add_pass(
                "Azure AI Search",
                {
                    "endpoint": endpoint[:50] + "...",
                    "index": index_name,
                    "status": str(response.status_code),
                    "elapsed_ms": str(elapsed_ms),
                },
            )
        else:
            result.add_fail(
                "Azure AI Search",
                f"Índice não encontrado ou acesso negado (HTTP {response.status_code})",
                {"index": index_name},
            )
    except requests.Timeout:
        result.add_fail(
            "Azure AI Search",
            f"Timeout na conexão (>{timeout}s)",
            {"endpoint": endpoint[:50] + "..."},
        )
    except Exception as e:
        result.add_fail(
            "Azure AI Search",
            f"{type(e).__name__}: {str(e)}",
        )


if __name__ == "__main__":
    main()
