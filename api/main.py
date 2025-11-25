import importlib
import pkgutil

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
from database import init_db
import routers  # importa o pacote raiz


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executa antes de a aplicação iniciar
    init_db()
    yield
    # Executa na finalização da aplicação (se quiser limpar algo)
    print("Encerrando aplicação...")

app = FastAPI(
    title="API do Sistema",
    lifespan=lifespan
)

# --- CONFIGURAÇÃO CORS ---
origins = [
    # A origem do seu frontend React. O número da porta é crucial!
    "http://localhost:5173",  
    "http://127.0.0.1:5173",
    # Opcional: Para permitir que o Swagger/Docs UI também funcione
    "http://localhost:8000",
]

# Adiciona o middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,              # Lista de origens permitidas
    allow_credentials=True,             # Permitir credenciais (cookies, tokens)
    allow_methods=["*"],                # Permitir todos os métodos (GET, POST, DELETE, etc.)
    allow_headers=["*"],                # Permitir todos os cabeçalhos
)

# Descobre e importa automaticamente todos os routers do pacote "routers"
for _, module_name, _ in pkgutil.walk_packages(routers.__path__, routers.__name__ + "."):
    module = importlib.import_module(module_name)
    print(f"Incluindo router do módulo: {module_name}")
    if hasattr(module, "router"):
        app.include_router(module.router)


@app.get("/api")
def root():
    return {"message": "API funcionando!"}


