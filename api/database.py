import os
from pathlib import Path
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text

# Carrega as variáveis do .env
load_dotenv()

# Monta a URL de conexão com o PostgreSQL
DATABASE_URL = (
    f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}"
    f"@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DBNAME')}"
)

SCHEMA_PATH = Path(__file__).parent / "schema.sql"
UPGRADE_PATH = Path(__file__).parent / "upgrade.sql"

print(DATABASE_URL)


# Cria o engine global (sem abrir conexão ainda)
engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    """Retorna uma sessão SQLModel (para ser usada no Depends do FastAPI)."""
    with Session(engine) as session:
        yield session


def init_db():
    
        # Verifica se já existe alguma tabela no schema público
    with engine.begin() as conn:

        tables_count = conn.scalar(text("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """))

        print(tables_count)

        if tables_count == 0:
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                conn.execute(text(f.read()))
            conn.commit()
            print("Banco inicializado com sucesso!")        

        else:
            print("Banco já inicializado. Nenhuma ação necessária.")

        with open(UPGRADE_PATH, "r", encoding="utf-8") as f:
            if  f.read().strip() == "":
                return
            f.seek(0)  # Volta ao início do arquivo
            conn.execute(text(f.read()))
        conn.commit()
        print("Banco atualizado com sucesso!")



    """Cria todas as tabelas definidas via SQLModel."""
    print("Inicializando banco via SQLModel...")
    SQLModel.metadata.create_all(engine)
    print("Banco inicializado com sucesso!")