from datetime import datetime
from sqlmodel import Session
from models import EntidadeAlvo, Historico, TipoOperacao

# Por enquanto armazena a operação como uma string
def add_to_log(
    db: Session,
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
    db.add(entry)
    db.commit()
