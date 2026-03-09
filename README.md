# Ecossistema Digital de Capacitação GRP (MVP Local)

Este repositório contém a versão MVP Local do Ecossistema de Capacitação GRP, focada nas interfaces de Busca e IA Simulada, utilizando Flask, SQLAlchemy e SQLite.

## Funcionalidades do MVP

O sistema foca em ser stateless e entregar as quatro interfaces aprovadas da PoC:
- **1. Repositório Linear**: Lista paginada de procedimentos com busca simples pelo título.
- **2. Sanfona (Accordion)**: Navegação hierárquica por Módulo > Tema > Subtema > Subsubtema.
- **6. Busca Mock**: Busca local por palavra-chave nos títulos, resumos e tags do material.
- **8. RAG Mock**: Simulação de IA generativa que resume os procedimentos listados, seguido pelas fontes.

## Pré-requisitos

Recomenda-se utilizar o [uv](https://github.com/astral-sh/uv) para gerenciamento do ambiente Python e execução ágil.
- Python 3.13+
- uv

## Como executar localmente

1. **Configure o ambiente**:
   ```bash
   cp .env.example .env
   ```
   (Você pode editar o `.env` caso queira mudar as portas ou URLs).

2. **Sincronize as dependências com `uv`**:
   ```bash
   uv sync
   ```

3. **Crie a base de dados via Alembic**:
   ```bash
   uv run alembic upgrade head
   ```

4. **Faça a importação inicial de dados (Seed via XLSX)**:
   ```bash
   uv run python scripts/import_data.py
   ```
   Isso criará os registros a partir de `data/imports/materials.xlsx`.

5. **Inicie a aplicação**:
   ```bash
   uv run flask run --debug
   ```
   A aplicação ficará disponível em http://127.0.0.1:5000.

## Como rodar os testes

Os testes são feitos em Pytest utilizando um banco SQLite em memória.
```bash
PYTHONPATH=. uv run pytest
```
