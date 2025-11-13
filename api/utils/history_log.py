from datetime import datetime
from sqlmodel import Session
from models import Historico

# Por enquanto armazena a operação como uma string
def add_to_log(
    db: Session,
    operation: str
):
    entry = Historico(
        created_at=datetime.now(),
        operation=operation
    )
    db.add(entry)
    db.commit()
