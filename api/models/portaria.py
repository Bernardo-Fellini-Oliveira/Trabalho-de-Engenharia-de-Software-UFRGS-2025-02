from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date, datetime

class Portaria(SQLModel, table=True):
    id_portaria: Optional[int] = Field(default=None, primary_key=True)
    numero: int
    data_portaria: date
    observacoes: Optional[str] = None
    ativo: bool = Field(default=True)
