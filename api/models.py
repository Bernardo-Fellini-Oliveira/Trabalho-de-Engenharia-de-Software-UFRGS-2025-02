from enum import Enum as PyEnum
from pydantic import BaseModel
from sqlmodel import JSON, Column, SQLModel, Field
from typing import Any, Dict, List, Optional
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


#Enums de tipo de operação e entidades para o histórico
class TipoOperacao(str, PyEnum):
    ADICAO = "Adição"
    REMOCAO = "Remoção"
    INATIVACAO = "Inativação"
    REATIVACAO = "Reativação"
    ASSOCIACAO = "Associação"
    FINALIZACAO = "Finalização" 

class EntidadeAlvo(str, PyEnum):
    PESSOA = "Pessoa"
    ORGAO = "Órgão"
    COMISSAO = "Comissão"
    CARGO = "Cargo"
    PORTARIA = "Portaria"
    OCUPACAO = "Ocupação"


class Historico(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)

    tipo_operacao: TipoOperacao
    entidade_alvo: EntidadeAlvo

    operation: str

#Tipo de retorno do histórico
class HistoricoModel(BaseModel):
    limite: int
    deslocamento: int
    total_itens: int
    historico: List[Historico]

class Status(str, PyEnum):
    PENDENTE = "Pendente"
    APROVADO = "Aprovado"
    REPROVADO = "Reprovado"

class Notificacoes(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Metadados
    data_solicitacao: datetime = Field(default_factory=datetime.now)
    operation: str
    
    # O que precisa ser feito (Reflete os Enums do Historico)
    tipo_operacao: TipoOperacao 
    entidade_alvo: EntidadeAlvo
        
    dados_payload: Dict[str, Any] = Field(sa_column=Column(JSON))

    # Status
    status_aprovacao: Status = Field(default=Status.PENDENTE)
    
    # Campos de Auditoria
    aprovador_id: Optional[int] = None
    data_aprovacao: Optional[datetime] = None
