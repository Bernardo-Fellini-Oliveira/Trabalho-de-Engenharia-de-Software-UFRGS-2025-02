from datetime import date
from fastapi import APIRouter, HTTPException, Path, Query, Depends
from sqlmodel import Field, SQLModel, Session, select
from database import get_session  # função que deve retornar Session()
from typing import Optional, List
from models import Portaria

router = APIRouter(
    prefix="/api/portaria",
    tags=["Portaria"]
)



@router.get("/", response_model=List[Portaria])
def carregar_portarias(session: Session = Depends(get_session)):
    """Carrega todas as portarias do banco de dados."""
    try:
        portarias = session.exec(select(Portaria)).all()
        return portarias
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar Portarias: {str(e)}")


@router.post("/", response_model=Portaria)
def adicionar_portaria(portaria: Portaria, session: Session = Depends(get_session)):
    """Adiciona uma nova portaria ao banco de dados."""
    try:
        session.add(portaria)
        session.commit()
        session.refresh(portaria)
        return portaria
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar Portaria: {str(e)}")


@router.delete("/delete/{id_portaria}")
def remover_portaria(
    id_portaria: int = Path(..., description="ID da Portaria a ser removida"),
    soft: bool = Query(False, description="Se 'true', realiza soft delete (define ativo=False). Se 'false', realiza hard delete."),
    session: Session = Depends(get_session)
):
    """Remove (ou inativa) uma portaria pelo seu ID."""
    try:
        portaria = session.get(Portaria, id_portaria)
        if not portaria:
            raise HTTPException(status_code=404, detail=f"Portaria com ID {id_portaria} não encontrada.")

        if soft:
            if not portaria.ativo:
                raise HTTPException(status_code=404, detail=f"Portaria com ID {id_portaria} já está inativa.")
            portaria.ativo = False
            session.add(portaria)
        else:
            session.delete(portaria)

        session.commit()
        return {"status": "success", "message": f"Portaria com ID {id_portaria} {'inativada' if soft else 'removida'} com sucesso."}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover Portaria: {str(e)}")


@router.put("/reativar/{id_portaria}")
def reativar_portaria(
    id_portaria: int = Path(..., description="ID da Portaria a ser reativada"),
    session: Session = Depends(get_session)
):
    """Reativa uma portaria inativa pelo seu ID."""
    try:
        portaria = session.get(Portaria, id_portaria)
        if not portaria:
            raise HTTPException(status_code=404, detail=f"Portaria com ID {id_portaria} não encontrada.")
        if portaria.ativo:
            raise HTTPException(status_code=400, detail=f"Portaria com ID {id_portaria} já está ativa.")

        portaria.ativo = True
        session.add(portaria)
        session.commit()
        return {"status": "success", "message": f"Portaria com ID {id_portaria} reativada com sucesso."}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao reativar Portaria: {str(e)}")