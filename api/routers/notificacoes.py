from datetime import date
from fastapi import APIRouter, HTTPException, Path, Query, Depends
from sqlmodel import Field, SQLModel, Session, select
from utils.history_log import add_to_log
from database import get_session  # função que deve retornar Session()
from typing import Any, Dict, Optional, List
from models import EntidadeAlvo, Notificacoes, Ocupacao, TipoOperacao

router = APIRouter(
    prefix="/api/notificacoes",
    tags=["Notificações"]
)



@router.get("/", response_model=List[Notificacoes])
def carregar_notificacoes(session: Session = Depends(get_session)):
    """Carrega todas as portarias do banco de dados."""
    try:
        notificacoes = session.exec(select(Notificacoes)).all()
        return notificacoes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar Notificações: {str(e)}")
    
@router.post("/aprovar/{id_ocupacao}", response_model=Notificacoes)
def aprovar_ocupacao(
    id_ocupacao: int = Path(..., description="ID da Notificação de Ocupação a ser aprovada"),
    session: Session = Depends(get_session)):
    try:

        notificacao = session.get(Notificacoes, id_ocupacao)
        if not notificacao:
            raise HTTPException(status_code=404, detail="Notificação não encontrado.")

        #data_payload: Dict[str, Any] = notificacao.dados_payload
        data_payload = notificacao.dados_payload

        if 'id_ocupacao' in data_payload:
        # Remove a chave primária do dicionário, permitindo que o banco a gere.
            del data_payload['id_ocupacao']

        if 'operation' in data_payload:
        # Remove a chave primária do dicionário, permitindo que o banco a gere.
            del data_payload['operation']

        nova_entidade = Ocupacao.model_validate(data_payload)

        session.add(nova_entidade)
        session.commit()
        session.refresh(nova_entidade)

        add_to_log(
            db=session,
            tipo_operacao=notificacao.tipo_operacao,
            entidade_alvo=notificacao.entidade_alvo,
            operation=nova_entidade.operation
        )
        
        return data_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao aprovar a notificação: {str(e)}")