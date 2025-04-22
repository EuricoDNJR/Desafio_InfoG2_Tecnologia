# Desafio_InfoG2_Tecnologia

![Badge em Desenvolvimento](http://img.shields.io/static/v1?label=STATUS&message=EM%20DESENVOLVIMENTO&color=GREEN&style=for-the-badge)![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white)![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)

## 📘 Descrição do Projeto

A **Lu Estilo** é uma empresa de confecção que está em busca de novas oportunidades de negócio. Atualmente, o time comercial enfrenta dificuldades devido à ausência de ferramentas que facilitem o acesso a novos canais de vendas.

### 💡 Solução Proposta

Como parte de um desafio técnico da empresa **InfoG2 Tecnologia**, foi proposta a criação de uma **API RESTful** desenvolvida em **Python com o framework FastAPI** e utilizando **PostgreSQL** como banco de dados.

Essa API tem como objetivo fornecer funcionalidades que facilitem a comunicação entre o time comercial, os clientes e a empresa, centralizando o gerenciamento de cadastros, produtos e pedidos.

## 🚀 Funcionalidades

### 🔐 Autenticação

- `POST /auth/register` — Cadastro de usuários
- `POST /auth/login` — Login de usuários
- `POST /auth/refresh-token` — Atualização do token de acesso

### 👤 Clientes

- `POST /clients/` — Cadastro de clientes
- `GET /clients/` — Listagem de todos os clientes
- `GET /clients/{client_id}` — Visualização de um cliente específico
- `PUT /clients/{client_id}` — Atualização de dados de um cliente
- `DELETE /clients/{client_id}` — Exclusão de cliente _(apenas admin)_

### 📦 Produtos

- `POST /products/` — Cadastro de produtos
- `GET /products/` — Listagem de todos os produtos
- `GET /products/{product_id}` — Visualização de um produto específico
- `PUT /products/{product_id}` — Atualização de dados de um produto
- `DELETE /products/{product_id}` — Exclusão de produto _(apenas admin)_

### 🧾 Pedidos

- `POST /orders/` — Cadastro de pedidos
- `GET /orders/` — Listagem de pedidos com filtros (período, cliente, seção, etc.)
- `GET /orders/{order_id}` — Visualização de um pedido específico
- `PUT /orders/{order_id}` — Atualização de pedido
- `DELETE /orders/{order_id}` — Exclusão de pedido _(apenas admin)_

## 📦 Pré-requisitos

Antes de executar a aplicação, é necessário garantir que o ambiente esteja devidamente configurado com os seguintes requisitos:

- Python 3.9+
- PostgreSQL (em execução e configurado no arquivo `.env`)
- Variáveis de ambiente no arquivo `.env`
- Pacotes listados em `requirements.txt`

### 📁 Arquivo `.env`

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis (exemplo):

```env
TEST=ON
ENV=dev
DATABASE_URL=your_database_url
TEST_DB_URL=your_test_database_url

FIREBASE_API_KEY=your_api_key
FIREBASE_AUTH_DOMAIN=your_auth_domain
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_bucket
FIREBASE_MESSAGING_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id
FIREBASE_MEASUREMENT_ID=your_measurement_id

FIREBASE_TYPE=service_account
FIREBASE_PRIVATE_KEY_ID=your_key_id
FIREBASE_PRIVATE_KEY="your_private_key"
FIREBASE_CLIENT_EMAIL=your_email
FIREBASE_CLIENT_ID=your_client_id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_CERT_URL=your_cert_url
FIREBASE_UNIVERSE_DOMAIN=googleapis.com
```

Onde TEST=ON significa que o jwt-token será sempre "test", e TEST=OFF significa que o jwt-token deverá ser o gerado por meio do Firebase. ENV=dev significa que o docs e o swagger estarão disponíveis, e ENV=prod significa que o docs e o swagger não estarão disponíveis.

### 🔧 Instalação de Dependências

Instale o pip:

```bash
sudo apt install python3-pip
```

Instale as dependências necessárias utilizando o `pip`:

```bash
pip install -r requirements.txt
```

### 🚀 Como Executar (modo local)

Para executar a aplicação em modo local, utilize o seguinte comando:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Acesse a aplicação em seu navegador através do seguinte endereço:

```bash
http://localhost:8080/docs
```

### 🐳 Como Executar (modo Docker)

Para executar a aplicação em modo Docker, utilize os seguintes comandos:

```bash
docker build -t lu-estilo-api .
docker run -d -p 8080:8080 lu-estilo-api
```

Acesse a aplicação em seu navegador através do seguinte endereço:

```bash
http://localhost:8080/docs
```

### 🐳 Como Executar (modo Docker Compose)

> ⚠️ **Atenção:** observe o arquivo `docker-compose.yml`. Ele irá criar dois bancos de dados: um para desenvolvimento e outro para testes automatizados.

Para executar a aplicação em modo Docker Compose, utilize os seguintes comandos:

```bash
docker-compose build
docker-compose up -d
```

Acesse a aplicação em seu navegador através do seguinte endereço:

```bash
http://localhost:8000/docs
```

## 🧪 Testes Automatizados

O projeto conta com uma suíte de testes automatizados utilizando o framework **Pytest**, garantindo a qualidade e o correto funcionamento das funcionalidades da API.

### 🔧 Preparação do Ambiente de Testes

Certifique-se de que o banco de dados de teste esteja configurado corretamente no arquivo `.env` com a variável `TEST_DB_URL`.

### ▶️ Como Executar os Testes

Você pode executar todos os testes automatizados com o seguinte comando:

```bash
pytest
```

### ✅ Estrutura dos Testes

Os testes estão organizados dentro da pasta `tests/` e cobrem os seguintes módulos:

- **Autenticação** (`auth`)
- **Clientes** (`clients`)
- **Produtos** (`products`)
- **Pedidos** (`orders`)

Cada módulo possui testes para **criação**, **leitura**, **atualização** e **exclusão** (CRUD), além de testes de **autorização** e **fluxo completo de uso**.

---

### 🧪 Ambiente Isolado

> ⚠️ **Atenção:** Os testes são executados utilizando um banco de dados separado (definido em `TEST_DB_URL`) para evitar interferência nos dados de desenvolvimento, então lembre-se de configurar `TEST`=`ON` no arquivo `.env`.

## 🚀 Deploy

O deploy da aplicação pode ser feito da seguinte forma: utilizando o **Docker** e o **Google Cloud Run**. Abaixo estão as instruções.

### 🐳 Docker

Para realizar o deploy utilizando **Docker**, siga os passos abaixo:

1. **Construir a imagem Docker**:

   Certifique-se de que você está na raiz do projeto e que o arquivo `Dockerfile` está configurado corretamente. Em seguida, execute o comando abaixo para construir a imagem:

   ```bash
   docker build -t lu-estilo-api .
   ```

2. **Rodar o container Docker**:

   Após a construção da imagem, você pode rodar o container utilizando o seguinte comando, para ver se está tudo certo:

   ```bash
   docker run -d -p 8080:8080 lu-estilo-api
   ```

3. **Acessar a aplicação**:

   Após rodar o container, você pode acessar a aplicação através do seguinte endereço:

   ```bash
   http://localhost:8080/docs
   ```

### ⚠️ Atenção: Sobre as Variáveis de Ambiente no Google Cloud Run

Durante o deploy no **Google Cloud Run**, é necessário utilizar um arquivo chamado `env-vars.yaml` em vez do `.env`.

Esse arquivo deve conter **as mesmas variáveis** definidas no `.env`, porém no formato aceito pelo Google Cloud, como no exemplo abaixo:

```yaml
ENV: "prod"
TEST: "OFF"
DATABASE_URL: "sua_url_do_banco"
TEST_DB_URL: "sua_url_do_banco_de_testes"
FIREBASE_API_KEY: "sua_chave"
FIREBASE_AUTH_DOMAIN: "seu_auth_domain"
FIREBASE_PROJECT_ID: "seu_project_id"
FIREBASE_STORAGE_BUCKET: "seu_bucket"
FIREBASE_MESSAGING_SENDER_ID: "seu_sender_id"
FIREBASE_APP_ID: "seu_app_id"
FIREBASE_MEASUREMENT_ID: "seu_measurement_id"
FIREBASE_TYPE: "service_account"
FIREBASE_PRIVATE_KEY_ID: "sua_key_id"
FIREBASE_PRIVATE_KEY: "sua_chave_privada"
FIREBASE_CLIENT_EMAIL: "seu_email"
FIREBASE_CLIENT_ID: "seu_client_id"
FIREBASE_AUTH_URI: "https://accounts.google.com/o/oauth2/auth"
FIREBASE_TOKEN_URI: "https://oauth2.googleapis.com/token"
FIREBASE_AUTH_PROVIDER_CERT_URL: "https://www.googleapis.com/oauth2/v1/certs"
FIREBASE_CLIENT_CERT_URL: "seu_cert_url"
FIREBASE_UNIVERSE_DOMAIN: "googleapis.com"
```

### 🐙 Deploy com Google Cloud Run

Se você deseja realizar o deploy da aplicação no Google Cloud Run, siga os passos abaixo:

1.  **Configuração do Google Cloud**:

    - Certifique-se de que você tem a CLI do Google Cloud instalada. Se não tiver, você pode instalá-la utilizando o comando:

      ```bash
      curl https://sdk.cloud.google.com | bash
      ```

    - Autentique-se na sua conta do Google Cloud:

      ```bash
      gcloud auth login
      ```

    - Defina seu projeto do Google Cloud:

      ```bash
      gcloud config set project <YOUR_PROJECT_ID>
      ```

2.  **Habilitar o Google Cloud Run**:

    Habilite o Google Cloud Run no seu projeto:

    ```bash
    gcloud services enable run.googleapis.com
    ```

3.  **Deploy da aplicação**:

    Após configurar o Google Cloud, você pode fazer o deploy da sua aplicação utilizando o seguinte comando:

    ```bash
    gcloud run deploy lu-estilo-api --source . --platform managed --region southamerica-east1 --allow-unauthenticated --env-vars-file env-vers.yaml
    ```

4.  **Acessar a aplicação**:
    Após o deploy, você receberá uma URL onde sua aplicação estará disponível.
