from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from models.pessoa import Pessoa
from database import get_session

router = APIRouter(prefix="/api/pessoa", tags=["Pessoa"])

# Listar pessoas
@router.get("/")
def carregar_pessoa(session: Session = Depends(get_session)):
    try:
        pessoas = session.exec(select(Pessoa)).all()
        return pessoas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar Pessoas: {e}")

# Criar pessoa
@router.post("/")
def adicionar_pessoa(pessoa: Pessoa, session: Session = Depends(get_session)):
    try:
        if not pessoa.nome.strip():
            raise HTTPException(status_code=400, detail="O nome da pessoa não pode ser vazio.")
        
        pessoa.ativo = True  # força ativo=1 na criação
        session.add(pessoa)
        session.commit()
        session.refresh(pessoa)
        return {
            "status": "success",
            "message": "Pessoa adicionada com sucesso",
            "id_pessoa": pessoa.id_pessoa
        }
    
    except IntegrityError as e:
        session.rollback()
        # checa se foi violação de unicidade
        error_code = getattr(e.orig, "pgcode", None)
        print(error_code)
        if error_code == '23505':  # código de erro para violação de unicidade no PostgreSQL
            raise HTTPException(
                status_code=409,
                detail="Já existe Pessoa com esse nome."
            )
        # outros erros de integridade
        raise HTTPException(400, f"Erro de integridade: {e}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar Pessoa: {e}")

# Soft ou Hard delete
@router.delete("/delete/{id_pessoa}")
def remover_pessoa(
    id_pessoa: int = Path(..., description="ID da Pessoa a ser removida"),
    soft: bool = Query(False, description="Se 'true', faz soft delete (ativo=0).")
    , session: Session = Depends(get_session)
):
    pessoa = session.get(Pessoa, id_pessoa)
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada.")

    if soft:
        if not pessoa.ativo:
            raise HTTPException(status_code=400, detail="Pessoa já está inativa.")
        pessoa.ativo = False
    else:
        try:
            session.delete(pessoa)
        except Exception as e:
            # caso haja vínculos (FK em Ocupação, por exemplo)
            raise HTTPException(
                status_code=400,
                detail=f"Não é possível remover esta pessoa pois há vínculos (Ocupações) ativos. {e}"
            )

    session.commit()
    return {
        "status": "success",
        "message": "Pessoa inativada (soft delete)." if soft else "Pessoa removida permanentemente."
    }

# Reativar pessoa
@router.put("/reativar/{id_pessoa}")
def reativar_pessoa(id_pessoa: int, session: Session = Depends(get_session)):
    pessoa = session.get(Pessoa, id_pessoa)
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada.")
    if pessoa.ativo:
        raise HTTPException(status_code=400, detail="Pessoa já está ativa.")

    pessoa.ativo = True
    session.commit()
    session.refresh(pessoa)
    return {"status": "success", "message": "Pessoa reativada com sucesso."}
