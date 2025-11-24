from datetime import datetime
from sqlmodel import Session
from models.historico import Historico
from utils.enums import EntidadeAlvo, TipoOperacao

# Por enquanto armazena a operação como uma string
def add_to_log(
    session: Session,
    operation: str,
    tipo_operacao: TipoOperacao,
    entidade_alvo: EntidadeAlvo
):
    entry = Historico(
        created_at=datetime.now(),
        operation=operation,
        tipo_operacao=tipo_operacao,
        entidade_alvo=entidade_alvo
    )
    session.add(entry)
    #session.commit()
