FROM python:3.13-slim

# Instalar dependências de SO necessárias para o PostgreSQL (psycopg2)
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar dependências e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto da codebase
COPY . .

# Expor a porta que o App Service espera (Geralmente 8000 para Gunicorn/Flask na Azure)
EXPOSE 8000

# Entrypoint usando Gunicorn para produção
# O gunicorn espera <modulo>:<variavel> ou <modulo>:<funcao_factory>()
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:create_app()"]
