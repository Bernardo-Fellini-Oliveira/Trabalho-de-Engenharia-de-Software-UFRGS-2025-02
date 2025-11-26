from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Orgao(SQLModel, table=True):
    id_orgao: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    ativo: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)