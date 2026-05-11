#!/usr/bin/env python
"""Teste simplificado de acesso aos modelos Azure OpenAI."""

import os
from pathlib import Path
from time import perf_counter

from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv(Path.cwd() / '.env')

print("\n" + "="*80)
print("TESTE DE DIAGNÓSTICO - ECOSSISTEMA GRP")
print("="*80)

print("\n[1] Verificando variáveis de ambiente...")
endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', 'NÃO CONFIGURADO')
deployment = os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT', 'NÃO CONFIGURADO')
print(f"    AZURE_OPENAI_ENDPOINT: {endpoint[:50]}...")
print(f"    AZURE_OPENAI_CHAT_DEPLOYMENT: {deployment}")

print("\n[2] Testando autenticação Entra ID...")
try:
    from app.search.azure_openai_client import AZURE_OPENAI_SCOPE, _build_openai_credential
    
    start = perf_counter()
    credential = _build_openai_credential()
    token = credential.get_token(AZURE_OPENAI_SCOPE)
    elapsed_ms = round((perf_counter() - start) * 1000, 2)
    
    print(f"    ✓ Token obtido com sucesso")
    print(f"      Tempo: {elapsed_ms}ms")
    print(f"      Token válido até: {token.expires_on}")
except Exception as e:
    print(f"    ✗ Falha na autenticação: {type(e).__name__}")
    print(f"      Erro: {str(e)}")
    exit(1)

print("\n[3] Testando chamada ao Azure OpenAI Chat...")
try:
    from app.search.azure_openai_client import build_azure_openai_client
    
    start = perf_counter()
    client = build_azure_openai_client()
    deployment = os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT')
    
    response = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": "OK"}],
        max_completion_tokens=5
    )
    elapsed_ms = round((perf_counter() - start) * 1000, 2)
    
    print(f"    ✓ Chat respondeu com sucesso")
    print(f"      Tempo: {elapsed_ms}ms")
    print(f"      Response ID: {response.id}")
    print(f"      Conteúdo: {response.choices[0].message.content[:50]}")
    
    print("\n" + "="*80)
    print("SUCESSO: Acesso aos modelos Azure OpenAI está funcionando!")
    print("="*80 + "\n")
    exit(0)
    
except ValueError as e:
    error_str = str(e)
    if "403" in error_str and "Virtual Network" in error_str:
        print(f"    ✗ FIREWALL/VNET BLOQUEANDO ACESSO")
        print(f"      Erro 403: {error_str[:100]}...")
        print(f"\n      Ação necessária:")
        print(f"      - Seu IP não está autorizado no firewall do Azure OpenAI")
        print(f"      - Contate o admin Azure/SEF-MG para liberar seu IP")
    else:
        print(f"    ✗ Erro de valor: {error_str}")
    exit(1)
    
except Exception as e:
    print(f"    ✗ Erro na chamada ao Azure OpenAI: {type(e).__name__}")
    print(f"      Erro: {str(e)[:150]}")
    exit(1)
