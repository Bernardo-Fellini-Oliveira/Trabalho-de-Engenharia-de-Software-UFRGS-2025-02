from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlmodel import Session, select
from typing import List
from models import Cargo
from database import get_session

router = APIRouter(prefix="/api/cargo", tags=["Cargo"])

# Criar cargo
@router.post("/", response_model=Cargo)
def adicionar_cargo(cargo: Cargo, session: Session = Depends(get_session)):
    try:
        session.add(cargo)
        session.commit()
        session.refresh(cargo)
        return cargo
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar Cargo: {e}")

# Listar cargos
@router.get("/", response_model=List[Cargo])
def carregar_cargo(session: Session = Depends(get_session)):
    try:
        return session.exec(select(Cargo)).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar Cargos: {e}")

# Soft ou Hard delete
@router.delete("/delete/{id_cargo}")
def remover_cargo(
    id_cargo: int = Path(..., description="ID do Cargo a ser removido"),
    soft: bool = Query(False, description="Se 'true', realiza soft delete (ativo=0)."),
    session: Session = Depends(get_session)
):
    cargo = session.get(Cargo, id_cargo)
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo não encontrado.")

    if soft:
        if not cargo.ativo:
            raise HTTPException(status_code=400, detail="Cargo já está inativo.")
        cargo.ativo = False
    else:
        try:
            session.delete(cargo)
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao remover Cargo: {e}. Verifique se há ocupações vinculadas."
            )

    session.commit()
    return {
        "status": "success",
        "message": "Cargo inativado (soft delete)." if soft else "Cargo removido permanentemente."
    }

# Reativar
@router.put("/reativar/{id_cargo}")
def reativar_cargo(
    id_cargo: int = Path(..., description="ID do Cargo a ser reativado"),
    session: Session = Depends(get_session)
):
    cargo = session.get(Cargo, id_cargo)
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo não encontrado.")
    if cargo.ativo:
        raise HTTPException(status_code=400, detail="Cargo já está ativo.")

    cargo.ativo = True
    session.commit()
    session.refresh(cargo)
    return {"status": "success", "message": "Cargo reativado com sucesso."}
