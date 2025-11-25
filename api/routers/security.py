from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi import Cookie, Depends, HTTPException, status, APIRouter
import os
from sqlmodel import Session, select
from models.user import UserTable, UserCreate as User # (Seu modelo de tabela, ex: UserTable)
from database import get_session
from models.role import UserRole


router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
    responses={404: {"description": "router problem"}},
)




SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1"))
except ValueError:
    ACCESS_TOKEN_EXPIRE_MINUTES = 1 
 
if not SECRET_KEY:
    raise RuntimeError("SECRET KEY não encontrada.")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None

class UserOut(BaseModel):
    username: str
    role: UserRole

    class Config:
        orm_mode = True


# Example of setting a proper hashed password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token") 


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        # Truncate the string to 72 characters, matching the hashing function's input
        password_str = str(plain_password)
        return pwd_context.verify(password_str, hashed_password)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    password_str = str(password)
    return pwd_context.hash(password_str)

def get_user(db: Session, username: str) -> UserTable | None:
    try:
        user_table_obj = db.exec(
            select(UserTable).where(UserTable.username == username)
        ).first()

        # Retorna a instância do UserTable diretamente
        return user_table_obj 
        
    except Exception as e:
        print(f"Erro ao buscar usuário com SQLModel: {e}")
        return None
        
    except Exception as e:
        print(f"Erro ao buscar usuário com SQLModel: {e}")
        return None # Trate erros de DB


def authenticate_user(db: Session, username: str, password: str): # Adiciona 'db'
    user = get_user(db, username) # Passa 'db' para get_user
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode = data.copy()
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



def register_user(db: Session, user_data: User):
    existing_user = db.exec(
        select(UserTable).where(UserTable.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome de usuário já registrado."
        )

    # 2. Hashear a Senha
    hashed_password = get_password_hash(user_data.password)

    # 3. Criar a instância do modelo SQLModel (Tabela)
    # Usa o **hashed_password** no objeto do banco
    db_user = UserTable(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        ativo=True,
        role=user_data.role
    )

    # 4. Salvar no Banco de Dados (PostgreSQL)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user) # Recarrega o objeto com o ID gerado pelo DB
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar no banco de dados: {e}"
        )

    # 5. Retornar os dados do usuário usando o modelo Pydantic seguro (User)
    # O SQLModel/FastAPI converte db_user (UserTable) para o Pydantic User, 
    # automaticamente ignorando o 'hashed_password'.
    return db_user

def role_required(required_role: str):
    def role_decorator(user: UserTable = Depends(get_current_user)):
        if user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return user
    return role_decorator

async def get_current_user(token: str = Depends(oauth_2_scheme), db: Session = Depends(get_session)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                         detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        token_data = TokenData(username=username)
        
    except JWTError:
        raise credential_exception

    user = get_user(db, username=token_data.username)
    if user is None:
        raise credential_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.ativo:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    print(f"Usuário autenticado: {current_user.username}, Role: {current_user.role}")
    return current_user


from fastapi.responses import JSONResponse

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})

    response = JSONResponse(content={
        "access_token": access_token,
        "token_type": "bearer"
    })

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        path="/api/auth/refresh"
    )

    return response


@router.post("/refresh")
async def refresh_access_token(
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_session)
):

    if refresh_token is None:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = get_user(db, username=username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    new_access = create_access_token({"sub": username})

    return {"access_token": new_access, "token_type": "bearer"}

@router.get("/users/me/", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    print("=========================")
    print(f"Usuário atual: {current_user.username}, Role: {current_user.role}")
    return current_user

@router.post("/register/", response_model=UserTable)
async def register_new_user(user: User, db: Session = Depends(get_session)):
    db_user = register_user(db, user)
    return db_user

@router.get("/only_admin", dependencies=[Depends(role_required(UserRole.ADMIN))])
async def get_only_admin():
    return True
