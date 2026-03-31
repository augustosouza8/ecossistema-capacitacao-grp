# Ecossistema Digital de Capacitação GRP (MVP Local)

Este repositório contém a versão inicial do Ecossistema de Capacitação GRP, focada nas interfaces de catálogo, busca e resposta assistida a partir do catálogo Excel.

O projeto está preparado para rodar localmente com `uv` ou com `pip`, usando Azure AI Search para busca textual/híbrida e Azure Blob Storage para acesso aos documentos.

## Funcionalidades do MVP

O sistema foca em ser stateless e entregar as quatro interfaces aprovadas da PoC:
- **1. Índice Geral (Repositório Linear)**: Lista paginada de procedimentos com busca simples pelo título.
- **2. Árvore de navegação (Sanfona / Accordion)**: Navegação hierárquica por Módulo > Tema > Subtema > Subsubtema.
- **3. Busca Semântica (tradicional)**: Busca local por palavra-chave nos títulos, resumos, tags e módulo do material.
- **4. Busca RAG (IA Generativa)**: Síntese local baseada nos itens mais aderentes do catálogo, seguida pelas fontes.

## Pré-requisitos

Recomenda-se utilizar o [uv](https://github.com/astral-sh/uv) para gerenciamento do ambiente Python e execução ágil.
- Python 3.13+
- uv
- ou `pip` + `venv`

## Variáveis de ambiente

1. Copie `/.env.example` para `/.env`.
2. Preencha, no mínimo:
   - `AZURE_SEARCH_ENDPOINT`
   - `AZURE_SEARCH_INDEX_NAME`
   - `AZURE_SEARCH_API_KEY`
   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_API_VERSION`
   - `AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT`
   - `AZURE_OPENAI_CHAT_DEPLOYMENT`
   - `AZURE_TENANT_ID`
   - `AZURE_CLIENT_ID`
   - `AZURE_CLIENT_SECRET`
3. Para downloads de documentos em ambiente local via Azure Blob, preencha tambem:
   - `AZURE_STORAGE_ACCOUNT_URL`

Observação: os arquivos `.docx` reais não são versionados no GitHub. O fluxo recomendado para testes locais é acessar os documentos via Azure Blob.

## Como executar localmente com uv

1. **Configure o ambiente**:
   ```bash
   cp .env.example .env
   ```
   (Você pode editar o `.env` caso queira mudar as portas ou URLs).

2. **Sincronize as dependências com `uv`**:
   ```bash
   uv sync
   ```

3. **Opcional: valide o catálogo Excel**:
   ```bash
   uv run python scripts/import_data.py
   ```

4. **Inicie a aplicação**:
   ```bash
    uv run flask run --debug
    ```
    A aplicação ficará disponível em http://127.0.0.1:5000.

## Como executar localmente com pip

1. **Crie e ative um ambiente virtual**:

   macOS/Linux:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   Windows PowerShell:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. **Configure o ambiente**:

   macOS/Linux:
   ```bash
   cp .env.example .env
   ```

   Windows PowerShell:
   ```powershell
   Copy-Item .env.example .env
   ```

3. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Opcional: valide o catálogo Excel**:
   ```bash
   python scripts/import_data.py
   ```

5. **Inicie a aplicação**:
   ```bash
   flask run --debug
   ```

## Execução local no Windows

- Instale Python 3.13+
- Instale `uv` ou use `pip`
- Copie `/.env.example` para `/.env`
- Preencha as credenciais Azure do seu ambiente
- Para testar downloads de POPs, use `AZURE_STORAGE_ACCOUNT_URL`, pois os `.docx` não estão no repositório
- Para testar a busca textual:
  - `http://127.0.0.1:5000/search?q=empenho&top=5`
- Para testar a busca híbrida:
  - `http://127.0.0.1:5000/search/hybrid?q=empenho&top=5`

## Como rodar os testes

Os testes usam uma planilha Excel temporária como fonte de catálogo.
```bash
PYTHONPATH=. uv run pytest
```

Com `pip`, use:
```bash
pytest
```

## Scripts de diagnóstico Azure

Os scripts abaixo ajudam a validar a autenticação no Azure OpenAI e o fluxo de busca:

```bash
uv run python scripts/check_openai_token.py
uv run python scripts/check_openai_embeddings.py
uv run python scripts/check_openai_chat.py
uv run python scripts/check_hybrid_search.py
```

Esses scripts também podem ser executados com `python` em um ambiente montado via `pip`.
