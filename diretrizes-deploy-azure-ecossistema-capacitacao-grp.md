# Diretrizes Oficiais de Deploy Azure: Ecossistema Capacitação GRP

> **Público-alvo:** Desenvolvedor(a) Júnior.
> **Objetivo:** Preparar e executar o deploy da aplicação "Ecossistema Digital de Capacitação GRP" na Microsoft Azure, partindo do estado atual (MVP Local) até uma arquitetura de nuvem segura baseada em Docker, PostgreSQL e Managed Identities.

---

## Sumário

1. [Estado atual da codebase vs. Arquitetura-alvo na Azure](#1-estado-atual-da-codebase-vs-arquitetura-alvo-na-azure)
2. [Decisões validadas para este deploy](#2-decisões-validadas-para-este-deploy)
3. [Explicação Prática para Iniciantes em Azure](#3-explicação-prática-para-iniciantes-em-azure)
4. [Arquivos da codebase que precisam ser alterados](#4-arquivos-da-codebase-que-precisam-ser-alterados)
5. [FASE 1: Refatorações na Codebase (Pré-Deploy)](#5-fase-1-refatorações-na-codebase-pré-deploy)
6. [FASE 1: Provisionamento da Infraestrutura na Azure](#6-fase-1-provisionamento-da-infraestrutura-na-azure)
7. [Estratégia de CI/CD (GitHub Actions com Docker)](#7-estratégia-de-cicd-github-actions-com-docker)
8. [Rotina de Inicialização (Migrações e Seed)](#8-rotina-de-inicialização-migrações-e-seed)
9. [Segurança, Rede e Monitoramento](#9-segurança-rede-e-monitoramento)
10. [FASE 2: Próximos Passos (Busca e IA)](#10-fase-2-próximos-passos-busca-e-ia)
11. [Rollback, Checklists e Troubleshooting](#11-rollback-checklists-e-troubleshooting)

---

## 1. Estado atual da codebase vs. Arquitetura-alvo na Azure

Antes de iniciarmos, é fundamental entender onde estamos e para onde vamos. Não tente subir o código na nuvem "do jeito que está", pois ele foi construído para rodar localmente.

**O Estado Real Hoje (MVP Mock Local):**
*   **Banco de Dados:** Utiliza SQLite (`local.db`), um banco em arquivo físico que gera erro de *Database Locked* se acessado simultaneamente por múltiplos usuários no App Service.
*   **Busca e RAG (IA):** A aplicação ainda não se comunica com a nuvem para isso. O arquivo `app/services/search_mock.py` simula as respostas de IA e a busca com base em texto simples.
*   **Arquivos (POPs):** Hospedados em uma pasta local (`data/docs/`).
*   **Dependências:** Faltam drivers nativos para o PostgreSQL e SDKs da Azure para Blob Storage, Identidade e IA.

**A Arquitetura-alvo na Azure:**
*   **Backend:** Um contêiner Docker rodando Flask + Gunicorn, hospedado no **Azure App Service**.
*   **Banco de Dados:** **Azure Database for PostgreSQL Flexible Server** (robusto, seguro, pronto para paralelismo).
*   **Arquivos:** **Azure Blob Storage**, servindo arquivos restritos via URLs temporárias seguras.
*   **Busca e IA (Fase 2):** Integração real com **Azure AI Search** e **Azure OpenAI**.

### 1.1. Validação do Runtime Python
A sua codebase exige **Python >= 3.13** (conforme definido no `pyproject.toml`). Essa é uma versão bem recente. Ao empacotar a aplicação em um contêiner Docker, garantimos previsibilidade: a mesma versão exata do Python que roda na sua máquina rodará na Azure, evitando erros de incompatibilidade de ambiente nativo de PaaS.

---

## 2. Decisões validadas para este deploy

Para garantir um deploy seguro e bem arquitetado, consolidamos as seguintes diretrizes:

1.  **Estratégia em Fases:** Faremos o deploy em duas etapas. A **Fase 1** (este documento) sobe a aplicação na Azure usando Docker, PostgreSQL e Blob Storage. A Busca e a IA continuam em modo `mock` para estabilizar a fundação. A **Fase 2** virará a chave da Inteligência Artificial.
2.  **Containerização (Docker) e `requirements.txt`:** Embora o Azure App Service suporte deploy via código diretamente, escolhemos **Docker** como estratégia principal por previsibilidade de ambiente. Além disso, usaremos o gerenciador `uv` para exportar um `requirements.txt` clássico. Isso não é uma limitação da Azure, mas uma **decisão arquitetural** nossa para padronizar a esteira de build do Docker de forma universal.
3.  **Managed Identity (Identidade Gerenciada):** Será o padrão de segurança. A aplicação usará o `DefaultAzureCredential` para acessar recursos da Azure sem precisar armazenar senhas ou chaves estáticas no código.
4.  **Blob Storage Privado com SAS URL:** O container de documentos `.docx` não será público. A aplicação Flask atuará como intermediária, gerando um link de acesso temporário (SAS Token) e redirecionando o usuário para o arquivo.
5.  **Exposição Inicial Pública:** O App Service inicial ficará aberto para a internet, estabelecendo uma linha de base funcional. Evoluções para fechamento de rede interna serão documentadas para o futuro.
6.  **Migrações Controladas:** A criação de tabelas (`alembic upgrade`) e a carga inicial de dados (`import_data.py`) **nunca** rodarão automaticamente no startup da aplicação. Serão processos controlados manualmente (ou em pipelines dedicados) para evitar corrupção e concorrência no banco.

---

## 3. Explicação Prática para Iniciantes em Azure

> **Dica para Júnior:** A nuvem corporativa organiza os serviços de forma lógica e segura. Compreender estes quatro conceitos é essencial para sua jornada:

*   **Resource Group (Grupo de Recursos):** Uma pasta lógica que agrupa todos os recursos de um mesmo projeto (ex.: `rg-grp-capacitacao-prod`). Facilita a gestão de custos e deleção (apagando o grupo, apagam-se todos os recursos vinculados).
*   **App Service (Web App for Containers):** É o serviço de hospedagem web. Em vez de você configurar uma máquina virtual (Linux/Windows) e gerenciar atualizações de OS, você simplesmente entrega a imagem Docker e a Azure cuida de mantê-la no ar.
*   **Azure Container Registry (ACR):** É o seu "DockerHub" privado. É o repositório seguro onde o GitHub Actions guardará sua imagem Docker pronta, aguardando o App Service puxá-la (pull) para rodar.
*   **Managed Identity (Identidade Gerenciada):** É a evolução das senhas. Trata-se de uma identidade registrada no **Microsoft Entra ID** (antigo Azure AD) que é atribuída automaticamente a um recurso (como o seu App Service). Em vez de colocar uma senha de banco ou chave de API no seu `.env`, você acessa o painel de IAM (Controle de Acesso) do recurso destino e diz: *"Dê a permissão (Role) de leitura para o App Service"*. A autenticação acontece silenciosamente nos bastidores pelos protocolos da Azure (Passwordless / RBAC), eliminando o vazamento de segredos no código.

---

## 4. Arquivos da codebase que precisam ser alterados

Antes de irmos para o portal da Azure, você precisará editar ou criar os seguintes arquivos no repositório:

1.  **`pyproject.toml`** (adicionar dependências de nuvem).
2.  **`requirements.txt`** (gerado via `uv export` para a construção do Docker).
3.  **`Dockerfile`** (criar na raiz para empacotar a aplicação).
4.  **`app/services/storage_service.py`** (novo arquivo para gerenciar os tokens de arquivos do Blob).
5.  **`app/routes/ui.py`** (ajustar as rotas de download para chamar o novo serviço de storage).
6.  **`.env.example`** (atualizar com os novos formatos de string de conexão e variáveis).
7.  **`.github/workflows/deploy.yml`** (criar a esteira de CI/CD).

---

## 5. FASE 1: Refatorações na Codebase (Pré-Deploy)

### 5.1. Adicionar dependências essenciais
Para conectar o Flask ao PostgreSQL e ao Azure Blob Storage de forma segura, adicione os drivers usando o seu gerenciador de dependências `uv`:

```bash
uv add psycopg2-binary
uv add azure-identity azure-storage-blob
uv add gunicorn
```
> **Nota de Consistência:** Utilizamos o `psycopg2-binary` pois ele se integra nativamente de forma muito madura com o SQLAlchemy, sendo padronizado também no backend e na URL de conexão.

### 5.2. Exportar o requirements.txt (Decisão Arquitetural)
Para que o contêiner Docker construa a imagem de forma limpa, compatível em qualquer pipeline, exportaremos as dependências para o formato padrão do pip:
```bash
uv export --format requirements-txt > requirements.txt
```

### 5.3. Criar a camada de SAS URL (Acesso Seguro a Arquivos)
Crie o arquivo `app/services/storage_service.py`. Esta função usará o `DefaultAzureCredential` (Identidade Gerenciada) para criar um link temporário seguro para os `.docx`, sem que o container Blob seja público.

```python
import os
from datetime import datetime, timedelta, timezone
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions

def get_blob_sas_url(blob_path: str) -> str:
    account_url = os.environ.get("AZURE_STORAGE_ACCOUNT_URL")
    container_name = "materials"
    
    # Usa Identidade Gerenciada na nuvem via Entra ID (ou seu Azure CLI login localmente)
    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(account_url, credential=credential)
    
    # Adquire uma chave de delegação do usuário (User Delegation Key)
    # Isso exige que a Managed Identity tenha a role "Storage Blob Delegator" no IAM do Storage
    udk = blob_service_client.get_user_delegation_key(
        key_start_time=datetime.now(timezone.utc),
        key_expiry_time=datetime.now(timezone.utc) + timedelta(hours=1)
    )

    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=container_name,
        blob_name=blob_path,
        user_delegation_key=udk,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.now(timezone.utc) + timedelta(minutes=15) # Validade de 15 minutos
    )

    return f"{account_url}/{container_name}/{blob_path}?{sas_token}"
```
*Na sua camada de rotas (`ui.py`), substitua o envio direto de arquivo estático por um redirecionamento (`return redirect(get_blob_sas_url(material.blob_path))`).*

### 5.4. Criar o Dockerfile e entender o comando de Startup
Crie o `Dockerfile` na raiz do projeto.

```dockerfile
FROM python:3.13-slim

# Bibliotecas de SO necessárias para compilar dependências do Postgres
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia toda a aplicação para dentro do contêiner
COPY . .

# Expõe a porta que o Azure App Service escutará
EXPOSE 8000

# Entrypoint via Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:app"]
```

**Por que o comando é `app:app`?**
O Gunicorn espera a sintaxe `<nome_do_modulo_python>:<nome_da_variavel_da_aplicacao>`. Na sua codebase, existe um arquivo `app.py` na raiz (o módulo é `app`). Dentro dele, você executa o código `app = create_app()` instanciando a aplicação na variável (a variável é `app`).

---

## 6. FASE 1: Provisionamento da Infraestrutura na Azure

### Passo 1: Azure Container Registry (ACR)
Crie um Container Registry (ex: `acrgrpcapacitacao`). Ele será o cofre seguro das suas imagens Docker.

### Passo 2: O Banco de Dados (PostgreSQL)
1. Crie um **Azure Database for PostgreSQL - Flexible Server**.
2. Defina `Admin username` e uma senha forte.
3. **Rede:** Como simplificação para este primeiro deploy funcional, em *Networking*, marque a opção **"Allow public access from any Azure service within Azure to this server"**. (Mais adiante, evoluiremos isso para redes privadas virtuais).

### Passo 3: O Storage de Arquivos
1. Crie uma **Storage Account** (Standard).
2. Em *Containers*, crie um chamado `materials` com nível de acesso **Private** (não permitir acesso anônimo em hipótese alguma).
3. Faça upload da estrutura de testes (ex: `materials/pops/101/arquivo.docx`).

### Passo 4: O App Service (Web App)
Crie um **Web App**. No *Publish*, selecione **Docker Container** e *Linux*. Na aba Docker, aponte para o seu ACR criado no Passo 1.

### Passo 5: Configurando a Segurança (Identidade Gerenciada e RBAC)
Este é o coração da arquitetura sem senhas.
1. No seu App Service recém-criado, vá em **Identity** (Identidade), ative o **System assigned** para "On" e salve.
2. Vá no seu **Container Registry (ACR)** > **Access Control (IAM)** > *Add role assignment* e dê a role de **AcrPull** para a Identidade do seu App Service. (Isso permite ao App puxar a imagem de forma autenticada).
3. Vá na sua **Storage Account** > **Access Control (IAM)** > *Add role assignment* e conceda à Identidade do App Service as duas permissões rigorosas necessárias para o SAS:
   - **Storage Blob Data Reader** (ou Contributor), para ler os documentos.
   - **Storage Blob Delegator**, para que a Managed Identity possa emitir tokens de permissão limitados para o usuário baixar os DOCX.

### Passo 6: Variáveis de Ambiente no App Service (Configuration)
Vá em *Environment variables* no App Service e configure:
*   `FLASK_ENV`: `production`
*   `SEARCH_PROVIDER`: `mock`
*   `WEBSITES_PORT`: `8000` *(Sinaliza que o Gunicorn escuta na 8000).*
*   `AZURE_STORAGE_ACCOUNT_URL`: `https://<nome-da-sua-storage-account>.blob.core.windows.net`
*   `DATABASE_URL`: `postgresql+psycopg2://<usuario>:<senha>@<nome-do-servidor-db>.postgres.database.azure.com:5432/<nome-do-banco-de-dados>`
    *   **Desmembrando a string do banco:**
        - `postgresql+psycopg2://`: Indica ao SQLAlchemy o dialeto e o driver instalados.
        - `<usuario>:<senha>`: O Admin e a senha criados na Azure.
        - `@<nome-do-servidor-db>.postgres.database.azure.com:5432`: O endereço DNS gerado pelo Flexible Server.
        - `/<nome-do-banco-de-dados>`: O nome do banco criado lá dentro (geralmente `postgres` ou outro se você customizou).

---

## 7. Estratégia de CI/CD (GitHub Actions com Docker)

Para builds e deploys seguros automáticos, configuraremos o GitHub Actions com credenciais OIDC (OpenID Connect federado) - garantindo segurança sem guardar senhas estáticas em Repositórios.

1. Configure credenciais federadas no Entra ID da Azure.
2. Crie no GitHub os Secrets: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, e `AZURE_SUBSCRIPTION_ID`. *(Em caráter opcional e estritamente para laboratórios simplificados provisórios, caso não consiga OIDC no momento, é possível ativar o painel de Access Keys/Admin User no ACR).*

Crie o workflow em `.github/workflows/deploy.yml`:

```yaml
name: Build e Deploy Azure

on:
  push:
    branches: [ "main" ]

permissions:
  id-token: write # Essencial para OIDC Autenticação Modern-Security
  contents: read

env:
  REGISTRY_NAME: acrgrpcapacitacao.azurecr.io
  IMAGE_NAME: ecossistema-grp
  WEBAPP_NAME: <nome-do-seu-app-service>

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Login na Azure via OIDC (Recomendado)
      uses: azure/login@v2
      with:
        client-id: ${{ secrets.AZURE_CLIENT_ID }}
        tenant-id: ${{ secrets.AZURE_TENANT_ID }}
        subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

    - name: Login no Azure Container Registry
      run: az acr login --name ${{ env.REGISTRY_NAME }}

    - name: Build e Push da Imagem Docker
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ env.REGISTRY_NAME }}/${{ env.IMAGE_NAME }}:${{ github.sha }}

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
    - name: Login na Azure via OIDC
      uses: azure/login@v2
      with:
        client-id: ${{ secrets.AZURE_CLIENT_ID }}
        tenant-id: ${{ secrets.AZURE_TENANT_ID }}
        subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

    - name: Atualiza a Imagem do App Service
      uses: azure/webapps-deploy@v3
      with:
        app-name: ${{ env.WEBAPP_NAME }}
        images: ${{ env.REGISTRY_NAME }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
```

---

## 8. Rotina de Inicialização (Migrações e Seed)

> **AVISO CRÍTICO:** As rotinas de migração do banco (`alembic`) e a carga de dados iniciais não devem ser atreladas ao startup/boot automático da aplicação. Isso evita cenários de *race condition* na nuvem.

### Opção A: Web SSH (Simples / Inicial)
1. No Portal Azure, vá até seu App Service > **SSH**. Ele abre o terminal *dentro* do contêiner instanciado.
2. Verifique se o `materials.xlsx` foi mapeado e execute:
   `alembic upgrade head`
   `python scripts/import_data.py`

### Opção B: Pipeline de Bootstrap (Controle Madura)
Para evolução de ambientes, pode-se criar um *Step* adicional no GitHub Actions ou numa máquina de jump/bastião que levanta um **Azure Container Instance (ACI)** isolado contendo sua imagem, roda `alembic upgrade` conectando-se ao seu PostgreSQL, e depois finaliza o container (Jobs e tarefas isoladas, sem perturbar o App Service).

---

## 9. Segurança, Rede e Monitoramento

### 9.1 Isolamento e Segurança de Rede
No deploy inicial, mantivemos as redes com IPs roteáveis para facilidade de diagnóstico.
**Caminho Evolutivo de Segurança:**
*   **VNet Integration:** Para travar acessos ao PostgreSQL, integramos o App Service a uma Virtual Network (Subnet) da Azure, e tornamos o DB privado.
*   **Private Endpoint/App Service Access Restrictions:** Se o uso for puramente de servidores corporativos estatais, fecharemos o inbound traffic com regras baseadas em IPs da rede do GRP.

### 9.2 Monitoramento, Logs e Observabilidade
Não deite no escuro após enviar o sistema ao ar. A infraestrutura em nuvem exige observabilidade.
1. Crie um recurso de **Application Insights**.
2. Adicione nas variáveis do App Service a chave: `APPLICATIONINSIGHTS_CONNECTION_STRING` usando a string obtida do portal.
*   **Diagnóstico e Performance:** Use a tela de Application Map e Transaction Diagnostics para verificar onde requisições SQL ou de leitura de Blob estão demorando (ex.: gargalos em query).
*   **Alertas Mínimos:** Configure disparo para HTTP 5xx (erros de servidor) e picos atípicos de CPU.
*   **Availability Test:** Crie um teste regular de *ping* que bate na URL `/` pública da sua aplicação a cada cinco minutos, alertando em caso de indisponibilidades.

---

## 10. FASE 2: Próximos Passos (Busca e IA)

O deploy atual estabelece uma infraestrutura base madura, mas as buscas e o RAG continuam rodando via mock. Para a virada da Fase 2, as alterações aprofundadas consistirão em:

1. **O que não existe e será programado:** A criação de `app/services/search_azure.py` (usando a SDK `azure-search-documents`) e `app/services/rag_service.py` (consumindo `openai`). Ambas substituirão as lógicas do mock.
2. **Provisionamento Novo:** Instalação e provisionamento de **Azure AI Search** e **Azure OpenAI/Foundry**.
3. **Novos Fluxos de Arquitetura:**
   - Será criado um **Indexer** no AI Search que lê periodicamente de forma direta o contêiner privado `materials` do Blob Storage.
   - Será implementada a configuração de *Integrated Vectorization*, fazendo o chunking e chamando silenciosamente os modelos de Embeddings do seu OpenAI durante a indexação.
4. **Variáveis de Ambiente Adicionais:** A chave `SEARCH_PROVIDER` virará `azure`. Adicionaremos as chaves `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_INDEX` entre outras.
5. **Autenticação da IA:** Não usaremos chaves API Key para OpenAI nem para o Search. A mesma *Managed Identity* receberá *Roles* suplementares como `Search Index Data Reader` e `Cognitive Services OpenAI User`.

---

## 11. Rollback, Checklists e Troubleshooting

### Como realizar um Rollback / Redeploy
Se um deploy através do GitHub Actions quebrar a produção, faça a reversão via Docker Image Tag:
1. No Portal Azure, acesse seu App Service > **Deployment Center** > Aba **Logs**. Identifique a falha e qual a última "tag de commit" bem-sucedida.
2. Nas variáveis de ambiente do App Service (ou na seção Configuration) modifique o apontamento de versão da imagem do seu ACR se aplicável, substituindo o hash atual defeituoso pelo hash anterior funcional. O contêiner é derrubado e o antigo sobre rapidamente intacto.

### Checklist Pós-Deploy de Sucesso
- [ ] O deploy e extração do container via ACR finalizou de forma correta sem timeouts?
- [ ] Conseguiu ler o Log Stream sem erros críticos do pacote `psycopg2-binary` e do `gunicorn`?
- [ ] As migrações rodaram perfeitamente com banco aceitando schema?
- [ ] A navegação pelas abas de catálogo renderiza de forma veloz?
- [ ] A abertura de POP (.docx) gerou com sucesso uma URL com credencial SASToken assinada dinamicamente com validades controladas?

### Troubleshooting (Os problemas mais frequentes)
*   **Aplicação em "Crash Loop" no boot:** Certifique-se da chave `WEBSITES_PORT=8000`. Conecte ao Log Stream, erros de importação revelam se você atualizou dependências com `uv` e se esqueceu de gerar o `requirements.txt` novo.
*   **BlobNotFound / Access Denied na SAS URL (Erro 403):** Ocorre frequentemente quando a função de `get_user_delegation_key` falha. O Azure RBAC propaga permissões com lentidão (5 a 15 minutos). Valide se as *roles* `Storage Blob Data Reader` e `Storage Blob Delegator` estão atribuídas diretamente à Managed Identity do seu App Service sobre aquele Storage Account em específico.
*   **Database Timeout:** A configuração de liberação pública "Allow public access from any Azure service" não propagou corretamente, ou a string `DATABASE_URL` formatou o porto (5432) errado.
