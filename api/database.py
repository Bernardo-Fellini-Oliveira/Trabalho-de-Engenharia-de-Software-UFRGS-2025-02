import psycopg2
from psycopg2 import sql
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()  # Carrega variáveis de ambiente do arquivo .env

# Caminho para o arquivo SQL com o schema
SCHEMA_PATH = Path("schema.sql")

DB_CONFIG = {
    "dbname": os.getenv("PG_DBNAME"),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
    "host": os.getenv("PG_HOST"),
    "port": os.getenv("PG_PORT"),
}


def get_connection():
    """Retorna uma conexão com o banco PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    """Cria as tabelas se ainda não existirem."""
    print("Inicializando o banco PostgreSQL...")
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Verifica se já existe alguma tabela no schema público
            cur.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """)
            tables_count = cur.fetchone()[0]

            if tables_count == 0:
                with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                    cur.execute(f.read())
                conn.commit()
                print("Banco inicializado com sucesso!")
            else:
                print("Banco já inicializado. Nenhuma ação necessária.")

            with open("upgrade.sql", "r", encoding="utf-8") as f:
                if  f.read().strip() == "":
                    return
                f.seek(0)  # Volta ao início do arquivo
                cur.execute(f.read())
            conn.commit()
            print("Banco atualizado com sucesso!")