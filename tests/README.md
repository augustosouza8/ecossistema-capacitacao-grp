## Estrutura de Testes - Ecossistema GRP

### 📁 Organização

Todos os testes agora estão centralizados na pasta `tests/`:

```
tests/
├── conftest.py                    # Configuração pytest (fixtures)
├── test_routes.py                 # Testes de rotas Flask
├── test_search.py                 # Testes de busca
├── __init__.py
├── diagnostics/                   # Testes de diagnóstico e validação
│   ├── diagnose.py               # Diagnóstico completo (conectividade, auth, etc)
│   ├── check_openai_token.py      # Valida obtenção de token Entra ID
│   ├── check_openai_chat.py       # Valida chat do Azure OpenAI
│   ├── check_openai_embeddings.py # Valida embeddings do Azure OpenAI
│   ├── check_network_endpoints.py # Valida conectividade com endpoints Azure
│   ├── check_entra_token_rest.py  # Valida token via REST API
│   ├── check_hybrid_search.py     # Valida busca híbrida
│   └── __init__.py
└── integration/                   # Testes de integração
    ├── test_azure_simple.py       # Teste de autenticação + chat
    ├── test_embeddings.py         # Teste de embeddings
    └── __init__.py
```

### 🚀 Como executar os testes

#### Testes unitários e de rota (usando pytest)
```bash
# Com uv
uv run pytest

# Com pip
pytest
```

#### Diagnóstico completo (conectividade + autenticação + LLM)
```bash
# Diagnóstico com todos os checks
uv run python tests/diagnostics/diagnose.py

# Com timeout customizado
uv run python tests/diagnostics/diagnose.py --timeout 10 --skip-search
```

#### Testes de diagnóstico individual
```bash
# Validar autenticação
uv run python tests/diagnostics/check_openai_token.py

# Validar chat
uv run python tests/diagnostics/check_openai_chat.py

# Validar embeddings
uv run python tests/diagnostics/check_openai_embeddings.py

# Validar rede (DNS, HTTPS)
uv run python tests/diagnostics/check_network_endpoints.py
```

#### Testes de integração
```bash
# Teste de autenticação + chat em um go
uv run python tests/integration/test_azure_simple.py

# Teste de geração de embeddings
uv run python tests/integration/test_embeddings.py
```

### 📋 Categorização dos testes

| Tipo | Localização | Propósito | Tempo |
|------|-------------|----------|-------|
| **Unitários** | `tests/test_*.py` | Validar funções individuais da app | ~1-5s |
| **Diagnóstico** | `tests/diagnostics/` | Verificar conectividade, auth, firewall | ~30s |
| **Integração** | `tests/integration/` | Testar modelos Azure OpenAI reais | ~5-10s |

### 🔧 Scripts de utilidade

Fora de `tests/`, na pasta `scripts/`:
- `import_data.py` — Importa dados do Excel para o catálogo (utilitário, não teste)

### ✅ Checklist de diagnóstico

Ao fazer setup do projeto, rode na ordem:

1. **Validar ambiente**
   ```bash
   uv run python tests/diagnostics/check_openai_token.py
   ```

2. **Validar conectividade**
   ```bash
   uv run python tests/diagnostics/check_network_endpoints.py
   ```

3. **Validar LLMs**
   ```bash
   uv run python tests/integration/test_azure_simple.py
   uv run python tests/integration/test_embeddings.py
   ```

4. **Diagnóstico completo**
   ```bash
   uv run python tests/diagnostics/diagnose.py
   ```

5. **Rodar testes da app**
   ```bash
   uv run pytest
   ```
