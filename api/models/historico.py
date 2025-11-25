from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field
from utils.enums import EntidadeAlvo, TipoOperacao


class Historico(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tipo_operacao: TipoOperacao
    entidade_alvo: EntidadeAlvo
    operation: str

#Tipo de retorno do histórico
class HistoricoModel(BaseModel):
    limite: int
    deslocamento: int
    total_itens: int
    historico: List[Historico]