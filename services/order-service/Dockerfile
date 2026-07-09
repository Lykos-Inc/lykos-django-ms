# Usa uma imagem base oficial do Python
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# --- CORREÇÃO AQUI ---
# Como o contexto do docker-compose é a raiz (.), precisamos especificar
# o caminho completo até o requirements.txt
COPY services/order-service/requirements.txt /app/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# --- CORREÇÃO AQUI TAMBÉM ---
# Copiamos apenas a pasta do serviço específico para dentro do container
# Se usássemos "COPY . /app/", ele copiaria o monorepo inteiro (auth, catalog, etc)
COPY services/order-service /app/

# Expõe a porta
EXPOSE 8000

CMD ["gunicorn", "order_service.wsgi:application", "--bind", "0.0.0.0:8000"]