# Como atualizar o catalogo real e os documentos locais

Este documento descreve o fluxo operacional atual do projeto, usando a planilha real em `data/imports/materials.xlsx` e os documentos reais em `data/docs/`.

## Visao geral

- A aplicacao le o catalogo diretamente de `data/imports/materials.xlsx`.
- Os documentos locais ficam em `data/docs/`.
- O catalogo atual usa `blob_path` para apontar para PDFs locais.
- Quando `AZURE_STORAGE_ACCOUNT_URL` esta configurada, o download e redirecionado para o Blob Storage.
- Quando essa variavel nao esta configurada, o app serve os arquivos diretamente de `data/docs/`.

## Estrutura da planilha

As colunas esperadas sao:

`id`, `type`, `title`, `module`, `theme`, `subtheme`, `subsubtheme`, `keywords`, `summary`, `source_url`, `blob_path`

Regras importantes:

- `id` deve ser numerico e unico.
- `title` e `module` nao podem ficar vazios.
- Itens com `blob_path` devem apontar para um arquivo existente em `data/docs/`.
- Itens com `source_url` devem apontar para um link valido.
- O app decide a acao da interface a partir de `blob_path` e `source_url`, nao mais de um tipo especifico como `POP` ou `VIDEO`.
- No catalogo real atual, todos os itens sao `MANUAL` e apontam para PDFs.

## Catalogo real atual

- Arquivo fonte: `data/imports/materials.xlsx`
- Total atual: `427` materiais
- Tipo predominante: `MANUAL`
- Modulo raiz atual: `Casos de Uso`
- Temas atuais:
  - `Institucional`
  - `Programacao Orcamentaria`
  - `Empenho e OLP`

## Atualizacao de documentos existentes

Use este fluxo quando houver uma nova versao de um documento ja catalogado.

1. Substitua o arquivo correspondente em `data/docs/`.
2. Se o nome do arquivo mudar, atualize tambem o `blob_path` na planilha.
3. Se o titulo ou a classificacao mudarem, atualize os metadados na linha correspondente.
4. Salve a planilha.
5. Rode a validacao:

```bash
uv run python scripts/import_data.py
```

## Inclusao de um novo documento local

1. Copie o PDF para `data/docs/`.
2. Abra `data/imports/materials.xlsx`.
3. Adicione uma nova linha com:
   - `id`: numero unico
   - `type`: valor descritivo do material, por exemplo `MANUAL`
   - `title`: nome exibido na interface
   - `module`: modulo principal
   - `theme`: agrupamento principal na arvore
   - `subtheme`: opcional
   - `subsubtheme`: opcional
   - `keywords`: termos relevantes separados por `;`
   - `summary`: resumo curto e objetivo
   - `source_url`: deixar vazio quando o arquivo for local
   - `blob_path`: nome exato do arquivo salvo em `data/docs/`
4. Salve a planilha.
5. Rode a validacao.

## Inclusao de uma referencia externa

O app ainda suporta materiais externos baseados em link.

1. Abra `data/imports/materials.xlsx`.
2. Adicione uma nova linha.
3. Preencha os metadados do material.
4. Em `source_url`, informe a URL externa.
5. Deixe `blob_path` vazio.
6. Salve a planilha e rode a validacao.

## Exclusao de um documento local

1. Remova a linha correspondente em `data/imports/materials.xlsx`.
2. Remova o arquivo correspondente de `data/docs/`.
3. Salve a planilha.
4. Rode a validacao.

## Checklist rapido

- Cada `blob_path` aponta para um arquivo existente em `data/docs/`.
- Nao ha `id` duplicado.
- O titulo esta claro para o usuario final.
- `keywords` e `summary` ajudam a busca local.
- A classificacao em `module`, `theme`, `subtheme` e `subsubtheme` faz sentido na navegacao.

## Comandos recomendados

### Validacao do catalogo

```bash
uv run python scripts/import_data.py
```

### Validacao completa do projeto

```bash
uv run ruff format && uv run ruff check --fix && uv run mypy . && uv run pytest
```

### Subir a aplicacao localmente

```bash
uv run flask run --debug
```

Depois, verificar:

- `http://127.0.0.1:5000/1_indice_geral`
- `http://127.0.0.1:5000/2_arvore_navegacao`
- `http://127.0.0.1:5000/3_busca_semantica?q=empenho`
- `http://127.0.0.1:5000/4_busca_rag?q=empenho`

## Migracao a partir de `padronizacao_planilha`

Quando for necessario refazer a carga com a base padronizada:

1. Copie `padronizacao_planilha/documentos_grp.xlsx` para `data/imports/materials.xlsx`.
2. Limpe `data/docs/`.
3. Copie os PDFs das pastas abaixo para `data/docs/`:
   - `padronizacao_planilha/processos_sei/SEI_1190.01.0017329_2025_61-Institucional`
   - `padronizacao_planilha/processos_sei/SEI_1190.01.0018032_2025_92-Progamacao-Orcamentaria`
   - `padronizacao_planilha/processos_sei/SEI_1190.01.0018063_2025_31-Empenho-OLP`
4. Rode as validacoes.
