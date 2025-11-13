from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from models import Historico
from database import get_session

router = APIRouter(prefix="/api/historico", tags=["Histórico de Operações"])


# Listar histórico
@router.get("/", response_model=List[Historico])
def carregar_cargo(session: Session = Depends(get_session)):
    try:
        return session.exec(select(Historico)).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar Cargos: {e}")