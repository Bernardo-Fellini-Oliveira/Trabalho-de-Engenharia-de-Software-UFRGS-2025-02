from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr
from models.role import UserRole


class UserCreate(BaseModel):
    username: str
    email: EmailStr | None = None
    password: str
    role: UserRole = UserRole.USUARIO

class UserTable(SQLModel, table=True):
    __tablename__ = "usuario"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str | None = None
    hashed_password: str = Field(nullable=False, exclude=True)
    ativo: bool = Field(default=True)
    role: UserRole = Field(default=UserRole.USUARIO)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)