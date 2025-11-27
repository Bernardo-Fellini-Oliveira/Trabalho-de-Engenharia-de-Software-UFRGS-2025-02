# Sistema de Gestão de Mandatos INF (API-First)


## ⚙️ Tecnologias Utilizadas

| Camada | Tecnologia | Linguagem    

| :-------- | :------------ | :---------- |   

| **Frontend** | React + Vite | TypeScript |

| **Backend** | FastAPI | Python |

| **Banco de Dados** | PostgreSQL | SQL |

---

## 1. Configuração do Ambiente e Banco de Dados


### 1.1. Configuração do PostgreSQL

O projeto utiliza o PostgreSQL. Instale o PostgreSQL [aqui](https://www.postgresql.org/download/) e faça as configurações necessárias. Lembre-se da sua senha e a porta configurada.
Após a instalação, lembre-se de colocar a pasta bin da instalação do PostgreSQL no PATH.

 **Antes de iniciar a API**, você deve criar o banco de dados.

1.  **Crie o Banco de Dados:** Use o `psql` ou o seu cliente de banco de dados favorito (ex: pgAdmin) para criar o banco de dados. No terminal, você pode rodar:

    ```
    psql -U postgres
    ```

    Insira a senha que você configurou durante a instalação. Agora para criar o banco rode:

    ```sql
    CREATE DATABASE meu_banco;
    ```


2.  **Atualize/Crie o `.env` da api:** Verifique se as credenciais no seu arquivo .env (dentro da pasta do Backend) estão corretas:

    ```python
    # Exemplo: Verifique a existência desse bloco no seu .env e configure com seus dados
    PG_DBNAME = "meu_banco"
    PG_USER = "postgres"
    PG_PASSWORD = "minha-senha-configurada"
    PG_HOST = "localhost"
    PG_PORT = 5432
    SECRET_KEY = "minha_senha_muito_secreta"
    ```

---

## 2. Instalação de Dependências

### 2.1. Backend (FastAPI - Python)

Navegue até a pasta do Backend (api/) (onde está o `main.py`).

1.  **Crie e Ative o Ambiente Virtual** (Opcional mas recomendado):
    ```bash
    python -m venv venv
    source venv/bin/activate  # macOS/Linux
    .\venv\Scripts\activate   # Windows
    ```
2.  **Instale as Dependências Python:**
    ```bash
    pip install -r requirements.txt
    ```

### 2.2. Frontend (React - Node.js)

Navegue até a pasta do Frontend (front/). Se você não tem o Node.js instalado, instale-o [aqui](https://nodejs.org/en/download)

1.  **Instale as Dependências Node:** 

    ```bash
    npm install
    npm install axios
    ```

---

## 3. Como Rodar a Aplicação (Build & Run)

A aplicação deve ser executada em dois terminais separados: um para o Backend e um para o Frontend.

### 3.1. Iniciar o Backend

No terminal do Backend e já na pasta do Backend (com ambiente virtual ativado, se tiver), rode:

```bash
uvicorn main:app --reload
```

### 3.2. Iniciar o Frontend

No terminal do Frontend e já na pasta do Frontend, rode:

```bash
npm run dev
```

## 4. Pronto!

A aplicação já deve estar rodando e acessível em http://localhost:5173
