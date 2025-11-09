from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date, datetime

class Cargo(SQLModel, table=True):
    id_cargo: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    ativo: bool = True
    id_orgao: int = Field(foreign_key="orgao.id_orgao")
    exclusivo: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)