from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, func, select
from typing import List, Optional
from models import EntidadeAlvo, Historico, HistoricoModel, TipoOperacao
from database import get_session

router = APIRouter(prefix="/api/historico", tags=["Histórico de Operações"])   

@router.get("/", response_model=HistoricoModel)
def carrega_historico(
    limite: int = Query(default=10, ge=1, le=50), #Padrão 10, mínimo 1, máximo 50
    deslocamento: int = Query(default=0, ge=0),     #Padrão 0

    filtro_operacao: Optional[List[TipoOperacao]] = Query(None, description="Filtrar por tipo(s) de operação."),
    
    filtro_entidade: Optional[List[EntidadeAlvo]] = Query(None, description="Filtrar por entidade(s) alvo."),

    session: Session = Depends(get_session)
):

    query_base = select(Historico)
        
    if filtro_operacao:
        query_base = query_base.where(Historico.tipo_operacao.in_(filtro_operacao))
    
    if filtro_entidade:
        query_base = query_base.where(Historico.entidade_alvo.in_(filtro_entidade))

    #Conta o total de itens após os filtros
    count_statement = select(func.count()).select_from(query_base.subquery())
    total_itens = session.exec(count_statement).one()
    
    #Consulta as entradas
    statement = (
        query_base
        .order_by(Historico.created_at.desc())
        .offset(deslocamento)
        .limit(limite)
    )
    
    historico_entradas = session.exec(statement).all()

    return HistoricoModel(
        limite=limite,
        deslocamento=deslocamento,
        total_itens=total_itens,
        historico=historico_entradas
    )