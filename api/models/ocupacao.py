from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date, datetime

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
