FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências do sistema
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Requirements
COPY services/catalog-service/requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Instala o shared (pacote compartilhado)
COPY shared /tmp/shared_pkg
RUN pip install --no-cache-dir /tmp/shared_pkg

# Código do serviço
COPY services/catalog-service .

EXPOSE 8000

CMD ["gunicorn", "catalog_service.asgi:application", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker"]