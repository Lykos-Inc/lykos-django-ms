FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências do sistema (libmagic é útil para validar uploads de arquivos)
RUN apt-get update \
    && apt-get install -y gcc libpq-dev libmagic1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY services/profile-service/requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Instala o pacote shared
COPY shared /tmp/shared_pkg
RUN pip install --no-cache-dir /tmp/shared_pkg

COPY services/profile-service .

EXPOSE 8000

CMD ["gunicorn", "profile_service.asgi:application", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker"]