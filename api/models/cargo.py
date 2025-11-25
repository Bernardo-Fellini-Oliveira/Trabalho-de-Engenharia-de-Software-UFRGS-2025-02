from sqlmodel import SQLModel, Field, UniqueConstraint
from typing import Optional
from datetime import date, datetime

print("Definindo modelo Cargo")

class Cargo(SQLModel, table=True):
    id_cargo: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    ativo: bool = True
    id_orgao: int = Field(foreign_key="orgao.id_orgao")
    exclusivo: bool = True
    substituto_para: Optional[int] = Field(default=None, foreign_key="cargo.id_cargo")
    substituto: Optional[int] = Field(default=None, foreign_key="cargo.id_cargo") 
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


    __table_args__ = (
        UniqueConstraint("nome", "id_orgao", name="uix_nome_orgao"),
    )