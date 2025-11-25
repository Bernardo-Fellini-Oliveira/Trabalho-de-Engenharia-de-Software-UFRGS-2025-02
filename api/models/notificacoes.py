from datetime import datetime
from typing import Any, Dict, Optional

from sqlmodel import JSON, Column, Field, SQLModel, String

from utils.enums import EntidadeAlvo, Status, TipoOperacao

class Notificacoes(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    data_solicitacao: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    operation: str
    tipo_operacao: TipoOperacao = Field(default=TipoOperacao.ASSOCIACAO)
    entidade_alvo: EntidadeAlvo = Field(default=EntidadeAlvo.OCUPACAO)
    dados_payload: Dict[str, Any] = Field(sa_column=Column(JSON))

    # Status
    status_aprovacao: Status = Field(default=Status.PENDENTE)
    
    regra: int 
    id_afetado: Optional[int] = None
    data_aprovacao: Optional[datetime] = None