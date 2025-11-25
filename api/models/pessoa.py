from sqlmodel import SQLModel, Field, UniqueConstraint
from typing import Optional
from datetime import date, datetime

class Pessoa(SQLModel, table=True):
    id_pessoa: int | None = Field(default=None, primary_key=True)
    nome: str
    ativo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("nome", name="uix_pessoa"),
    )