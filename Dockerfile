FROM python:3.12-slim

# Diretório interno onde o backend será executado dentro do container.
WORKDIR /app

# Dependências de sistema necessárias para instalar pacotes Python com PostgreSQL.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Instala as dependências sem cache para manter a imagem menor.
RUN pip install --no-cache-dir -r requirements.txt

# Copia somente o backend para que `main.py` e `init_db.py` fiquem na raiz de /app.
COPY backend/ .

# Porta padrão usada pelo Uvicorn no docker-compose.
EXPOSE 8000
