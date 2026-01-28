# Lykos Microservices (Django + Docker)

Este repositório contém a arquitetura de microsserviços para o marketplace Lykos, utilizando Django, DRF e Docker.

## 🚀 Como Iniciar

Siga os passos abaixo para configurar o ambiente de desenvolvimento local.

### 1. Variáveis de Ambiente e Configuração

O projeto utiliza arquivos de exemplo (`.example`) para não expor credenciais sensíveis. Você precisa criar suas versões locais destes arquivos.

1.  **Arquivo `.env`**:
    * Localize o arquivo `.env.example` na raiz.
    * Crie uma cópia chamada `.env`.
    * Preencha as variáveis (DB, chaves de API, etc).

2.  **Arquivo `docker-compose.yml`**:
    * Localize o `docker-compose.example.yaml`.
    * Crie uma cópia chamada `docker-compose.yml`.

3.  **Configuração do Traefik (JWT)**:
    * Vá até a pasta `traefik/dynamic/`.
    * Localize `jwt-middleware.example.yaml`.
    * Crie uma cópia chamada `jwt-middleware.yml`.
    * **Importante:** Abra este novo arquivo e garanta que a chave `secret` seja **idêntica** à variável `JWT_SECRET` definida no seu arquivo `.env`.

> ⚠️ **Nota:** Os arquivos novos (`.env`, `docker-compose.yml`, `jwt-middleware.yml`) já estão no `.gitignore` e não serão enviados para o repositório.

### 2. Executando o Projeto

Com os arquivos de configuração criados, inicie os containers:

```bash
docker compose up -d
```

O Traefik servirá como Gateway e os serviços estarão acessíveis através dele (ex: `localhost/api/auth`, `localhost/docs`).

---

## 📂 Estrutura do Projeto

Abaixo está a estrutura prevista para este monorepo:

```bash
lykos-django/
├── docker-compose.yml                 # Orquestração dos containers
├── .env                               # Variáveis de ambiente (Segredos)
├── traefik/                           # Configurações do Proxy Reverso
│   ├── traefik.yml                    # Configuração estática
│   ├── dynamic/                       # Configuração dinâmica
│   │   ├── jwt-middleware.yml         # Middleware de validação JWT
│   │   └── rate-limit.yml             # Limitação de requisições
│   └── acme.json                      # Certificados SSL (se houver)
│
├── services/                          # Microsserviços
│   ├── auth-service/                  ← Autenticação (Login, cadastro, JWT)
│   ├── profile-service/               ← Perfil (Freelancer, portfólio, uploads)
│   ├── catalog-service/               ← Catálogo (Gigs, categorias, pacotes)
│   ├── order-service/                 ← Pedidos (Pagamento AbacatePay, entregas)
│   ├── review-service/                ← Avaliações e Feedback
│   └── notification-service/          ← Notificações (E-mail, Push)
│
├── shared/                            ← Pacote Python compartilhado (Libs comuns)
│   ├── pyproject.toml
│   └── shared/
│       ├── __init__.py
│       ├── constants.py
│       ├── enums.py
│       ├── utils.py
│       ├── middlewares.py
│       └── exceptions.py
│
├── minio/                             ← Volume de armazenamento de arquivos (S3 Local)
├── postgres/                          ← Volume de dados do Banco
└── docs/                              ← Documentação OpenAPI agregada
```

---

## 🛠️ Tecnologias Principais

* **Linguagem:** Python 3.12
* **Framework:** Django & Django REST Framework
* **Banco de Dados:** PostgreSQL (Schemas isolados por serviço)
* **Infraestrutura:** Docker & Docker Compose
* **Gateway:** Traefik
* **Storage:** MinIO (Compatível com S3)
* **Pagamentos:** AbacatePay
