#!/usr/bin/env python
"""Teste de embeddings no Azure OpenAI."""

import os
import sys
from pathlib import Path
from time import perf_counter

print("Iniciando teste de embeddings...", flush=True)

from dotenv import load_dotenv

load_dotenv(Path.cwd() / '.env')

print("\nTestando Azure OpenAI Embeddings...", flush=True)

try:
    print("  Importando módulos...", flush=True)
    from app.search.azure_embeddings import AzureEmbeddingsService
    from app.search.azure_openai_client import build_azure_openai_client
    
    print("  Construindo cliente...", flush=True)
    start = perf_counter()
    client = build_azure_openai_client()
    service = AzureEmbeddingsService(client)
    
    print("  Gerando embedding...", flush=True)
    embedding = service.embed_query("teste de capacidade")
    elapsed_ms = round((perf_counter() - start) * 1000, 2)
    
    print(f"✓ Embeddings obtidos com sucesso", flush=True)
    print(f"  Tempo: {elapsed_ms}ms", flush=True)
    print(f"  Dimensões: {len(embedding)}", flush=True)
    print(f"  Preview (primeiros 5 valores): {embedding[:5]}", flush=True)
    sys.exit(0)
    
except Exception as e:
    print(f"✗ Erro nos embeddings: {type(e).__name__}", flush=True)
    print(f"  Erro: {str(e)[:150]}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
