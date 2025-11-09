import importlib
import pkgutil

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
from database import init_db
import routers  # importa o pacote raiz

import security as scrt
from datetime import timedelta
from fastapi import Depends, HTTPException, status



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

@app.post("/token", response_model=scrt.Token)
async def login_for_access_token(from_data: OAuth2PasswordRequestForm = Depends()):
    user = scrt.authenticate_user(scrt.fake_db, from_data.username, from_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=scrt.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = scrt.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=scrt.User)
async def read_users_me(current_user: scrt.User = Depends(scrt.get_current_active_user)):
    return current_user

