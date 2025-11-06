from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date, datetime

class Orgao(SQLModel, table=True):
    id_orgao: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    ativo: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Cargo(SQLModel, table=True):
    id_cargo: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    ativo: bool = True
    id_orgao: int = Field(foreign_key="orgao.id_orgao")
    exclusivo: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Ocupacao(SQLModel, table=True):
    id_ocupacao: Optional[int] = Field(default=None, primary_key=True)
    id_pessoa: int = Field(foreign_key="pessoa.id_pessoa")
    id_cargo: int = Field(foreign_key="cargo.id_cargo")
    id_portaria: Optional[int] = Field(foreign_key="portaria.id_portaria")
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    mandato: int
    observacoes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Pessoa(SQLModel, table=True):
    id_pessoa: int | None = Field(default=None, primary_key=True)
    nome: str
    ativo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Portaria(SQLModel, table=True):
    id_portaria: Optional[int] = Field(default=None, primary_key=True)
    numero: int
    data_portaria: date
    observacoes: Optional[str] = None
    ativo: bool = Field(default=True)

