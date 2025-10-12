import sqlite3
from pathlib import Path

DB_PATH = Path("Banco.db")
SCHEMA_PATH = Path("schema.sql")

def get_connection():
    """Retorna uma conexão com o banco."""
    return sqlite3.connect(DB_PATH)

def init_db():
    """Cria o banco e as tabelas se ainda não existirem."""
    if not DB_PATH.exists():
        print("Criando Banco.db...")
        with get_connection() as conn:
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
        print("Banco.db criado com sucesso!")
    else:
        print("Banco.db já existe — nenhuma ação necessária.")
