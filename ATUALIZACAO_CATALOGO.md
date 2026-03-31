# Como atualizar arquivos, videos e a `materials.xlsx`

Este documento descreve o processo operacional para manter o catalogo atualizado nesta fase do projeto, em que a fonte de verdade e a planilha `data/imports/materials.xlsx`.

## Visao geral

- A aplicacao le o catalogo diretamente de `data/imports/materials.xlsx`.
- Os arquivos de documentos ficam em `data/docs/`.
- Itens do tipo `POP` usam `blob_path` para localizar o arquivo.
- Itens do tipo `VIDEO` usam `source_url` para abrir o link do video.
- Sempre que houver inclusao, alteracao ou exclusao, a planilha deve ser atualizada para refletir exatamente o estado desejado do catalogo.

## Estrutura da planilha

As colunas esperadas atualmente sao:

`id`, `type`, `title`, `module`, `theme`, `subtheme`, `subsubtheme`, `keywords`, `summary`, `source_url`, `blob_path`

Regras importantes:

- `id` deve ser numerico e unico.
- `type` deve ser `POP` ou `VIDEO`.
- `title` e `module` nao podem ficar vazios.
- `POP` deve ter `blob_path` preenchido.
- `VIDEO` deve ter `source_url` preenchido.
- `keywords` e `summary` devem ser preenchidos sempre que possivel para melhorar busca e RAG.

## 1. Inclusao de um novo arquivo POP

Use este fluxo quando um novo procedimento em documento precisar entrar no catalogo.

### Passo a passo

1. Copie o arquivo `.docx` para `data/docs/`.
2. Use um nome padronizado e estavel para o arquivo, por exemplo:
   - `POP_123__empenho-inclusao-ordinario.docx`
3. Abra `data/imports/materials.xlsx`.
4. Adicione uma nova linha ao final da planilha.
5. Preencha os campos:
   - `id`: numero unico
   - `type`: `POP`
   - `title`: nome exibido na interface
   - `module`: modulo principal
   - `theme`: tema
   - `subtheme`: subtema
   - `subsubtheme`: detalhamento adicional, se existir
   - `keywords`: palavras de busca separadas por `;`
   - `summary`: resumo objetivo do procedimento
   - `source_url`: deixar vazio
   - `blob_path`: nome exato do arquivo salvo em `data/docs/`
6. Salve a planilha.
7. Valide o catalogo:
   ```bash
   uv run python scripts/import_data.py
   ```
8. Verifique a exibicao na aplicacao:
   - `http://127.0.0.1:5000/1_indice_geral`
   - `http://127.0.0.1:5000/2_arvore_navegacao`
   - `http://127.0.0.1:5000/3_busca_semantica?q=<termo>`
   - `http://127.0.0.1:5000/4_busca_rag?q=<termo>`

### Checklist rapido

- O arquivo existe em `data/docs/`.
- O `blob_path` bate exatamente com o nome do arquivo.
- O `id` nao se repete.
- O item aparece nas telas.

## 2. Inclusao de um novo video

Use este fluxo quando o material for hospedado externamente e acessado por link.

### Passo a passo

1. Abra `data/imports/materials.xlsx`.
2. Adicione uma nova linha.
3. Preencha os campos:
   - `id`: numero unico
   - `type`: `VIDEO`
   - `title`: titulo exibido
   - `module`: modulo principal
   - `theme`: tema
   - `subtheme`: subtema
   - `subsubtheme`: detalhamento adicional, se existir
   - `keywords`: termos de busca
   - `summary`: resumo do conteudo
   - `source_url`: URL do video
   - `blob_path`: deixar vazio
4. Salve a planilha.
5. Valide o catalogo:
   ```bash
   uv run python scripts/import_data.py
   ```
6. Verifique a exibicao e o link do video nas interfaces.

### Checklist rapido

- O `source_url` abre corretamente.
- O `blob_path` ficou vazio.
- O video aparece nas buscas.

## 3. Atualizacao de um arquivo POP existente

### Quando so os metadados mudam

Edite apenas a linha correspondente na `materials.xlsx`:

- `title`
- `module`
- `theme`
- `subtheme`
- `subsubtheme`
- `keywords`
- `summary`

Depois salve e valide com:

```bash
uv run python scripts/import_data.py
```

### Quando o documento tambem muda

1. Substitua o arquivo em `data/docs/`.
2. Se o nome do arquivo continuar igual, mantenha o mesmo `blob_path`.
3. Se o nome mudar, atualize tambem o `blob_path` na planilha.
4. Salve a planilha.
5. Valide o catalogo e teste o download pela interface.

## 4. Atualizacao de um video existente

1. Localize a linha correspondente na `materials.xlsx`.
2. Atualize os campos necessarios, normalmente:
   - `title`
   - `keywords`
   - `summary`
   - `module`
   - `theme`
   - `subtheme`
   - `subsubtheme`
   - `source_url`
3. Salve a planilha.
4. Rode a validacao.
5. Teste o acesso ao video nas telas de busca e RAG.

## 5. Exclusao de um arquivo POP

Para remover um documento do catalogo, o ajuste deve ser feito em dois lugares.

### Passo a passo

1. Remova a linha correspondente em `data/imports/materials.xlsx`.
2. Remova o arquivo correspondente de `data/docs/`.
3. Salve a planilha.
4. Rode a validacao:
   ```bash
   uv run python scripts/import_data.py
   ```
5. Verifique se o item nao aparece mais nas interfaces.

### Importante

Se voce apagar apenas a linha da planilha e deixar o arquivo em `data/docs/`, o catalogo nao quebra, mas sobra arquivo sem uso.

Se voce apagar apenas o arquivo e deixar a linha na planilha, a interface continuara exibindo o item, mas o download falhara.

## 6. Exclusao de um video

1. Remova a linha correspondente em `data/imports/materials.xlsx`.
2. Salve a planilha.
3. Rode a validacao.
4. Verifique se o item desapareceu das telas.

## 7. Regras de consistencia operacional

Antes de considerar qualquer atualizacao concluida, confirme:

- Cada linha representa exatamente um item real do catalogo.
- Nao existe `id` duplicado.
- Todo `POP` aponta para um arquivo existente.
- Todo `VIDEO` aponta para um link valido.
- O titulo esta claro para o usuario final.
- O resumo ajuda a busca e a resposta RAG.
- A classificacao em `module`, `theme`, `subtheme` e `subsubtheme` faz sentido para a navegacao em arvore.

## 8. Comandos recomendados apos qualquer alteracao

### Validacao minima do catalogo

```bash
uv run python scripts/import_data.py
```

### Validacao completa do projeto

```bash
uv run ruff format && uv run ruff check --fix && uv run mypy . && uv run pytest
```

### Subir a aplicacao localmente para validacao manual

```bash
uv run flask run --debug
```

Depois, verificar:

- `http://127.0.0.1:5000/1_indice_geral`
- `http://127.0.0.1:5000/2_arvore_navegacao`
- `http://127.0.0.1:5000/3_busca_semantica?q=<termo>`
- `http://127.0.0.1:5000/4_busca_rag?q=<termo>`

## 9. Exemplo de preenchimento

### Exemplo de POP

| id | type | title | module | theme | subtheme | subsubtheme | keywords | summary | source_url | blob_path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 501 | POP | Empenho - Inclusao Ordinario | Empenho | Inclusao | Ordinario |  | empenho; inclusao; ordinario | Passo a passo para incluir um empenho ordinario. |  | POP_501__empenho-inclusao-ordinario.docx |

### Exemplo de VIDEO

| id | type | title | module | theme | subtheme | subsubtheme | keywords | summary | source_url | blob_path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 502 | VIDEO | Video - Tipos de Empenho | Empenho | Conceitos |  |  | empenho; video; conceitos | Video introdutorio sobre os tipos de empenho. | https://example.com/video-tipos-empenho |  |

## 10. Resumo operacional

- Se entrou item novo, atualize a planilha.
- Se entrou documento, atualize tambem `data/docs/`.
- Se saiu documento, remova da planilha e da pasta.
- Se saiu video, remova da planilha.
- Sempre valide a planilha.
- Sempre teste as telas principais antes de publicar a alteracao.
