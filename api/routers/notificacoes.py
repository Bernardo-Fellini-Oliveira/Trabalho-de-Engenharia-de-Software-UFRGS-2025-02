from datetime import date
import datetime
from fastapi import APIRouter, HTTPException, Path, Query, Depends
from sqlmodel import Field, SQLModel, Session, select
from models.cargo import Cargo
from models.orgao import Orgao
from models.pessoa import Pessoa
from utils.history_log import add_to_log
from database import get_session  # função que deve retornar Session()
from typing import Any, Dict, Optional, List
from models.notificacoes import Notificacoes
from models.ocupacao import Ocupacao
from utils.enums import EntidadeAlvo, Status, TipoOperacao

router = APIRouter(
    prefix="/api/notificacoes",
    tags=["Notificações"]
)



@router.get("/", response_model=List[Notificacoes])
def carregar_notificacoes(session: Session = Depends(get_session)):

    try:
        notificacoes = session.exec(select(Notificacoes)).all()
        return notificacoes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar Notificações: {str(e)}")
    
@router.post("/aprovar/{id_ocupacao}")
def aprovar_ocupacao(
    id_ocupacao: int = Path(..., description="ID da Notificação de Ocupação a ser aprovada"),
    approve: bool = Query(True, description="Se 'true', aprova notificação (ativo=0)."),
    session: Session = Depends(get_session)):
    try:
        notificacao = session.get(Notificacoes, id_ocupacao)
        if not notificacao:
            raise HTTPException(status_code=404, detail="Notificação não encontrado.")
        if notificacao.status_aprovacao != Status.PENDENTE:
            raise HTTPException(status_code=400, detail="Notificação já foi processada")
        #data_payload: Dict[str, Any] = notificacao.dados_payload
        data_payload = notificacao.dados_payload
        nova_entidade = Ocupacao.model_validate(data_payload)

        if approve:
            cargo = session.get(Cargo, nova_entidade.id_cargo)
            pessoa = session.get(Pessoa, nova_entidade.id_pessoa)
            orgao = session.get(Orgao, cargo.id_orgao)

            notificacao.status_aprovacao = Status.APROVADO
            notificacao.data_aprovacao = datetime.now()
            session.add(nova_entidade)
            add_to_log(
                session=session,
                tipo_operacao=notificacao.tipo_operacao,
                entidade_alvo=notificacao.entidade_alvo,
                operation=f"[ADD] Adicionada ocupação de {pessoa.nome} no cargo de {cargo.nome}, no órgão {orgao.nome}." 
            )
            session.commit()
            session.refresh(nova_entidade)
            session.refresh(notificacao)
            return {
                "status": "success",
                "message": "Notificação aprovada com sucesso"
            }
        else:
            notificacao.status_aprovacao = Status.RECUSADO
            session.refresh(notificacao)
            session.commit()
            return {
                "status": "success",
                "message": "Notificação rejeitada com sucesso"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao aprovar a notificação: {str(e)}")