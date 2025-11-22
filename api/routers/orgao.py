from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlmodel import Session, select
from utils.history_log import add_to_log
from models import EntidadeAlvo, Orgao, TipoOperacao
from database import get_session

router = APIRouter(prefix="/api/orgao", tags=["Órgão"])

# Criar órgão
@router.post("/")
def adicionar_orgao(orgao: Orgao, session: Session = Depends(get_session)):
    try:
        session.add(orgao)
        session.commit()
        session.refresh(orgao)
        add_to_log(
            db=session,
            tipo_operacao=TipoOperacao.ADICAO,
            entidade_alvo=EntidadeAlvo.ORGAO,
            operation=f"[ADD] O Órgão {orgao.nome} foi adicionado(a)",
        )   
        return {
            "status": "success",
            "message": "Órgão adicionado com sucesso",
            "id_orgao": orgao.id_orgao
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar Órgão: {e}")

# Listar órgãos
@router.get("/")
def carregar_orgao(session: Session = Depends(get_session)):
    try:
        orgaos = session.exec(select(Orgao)).all()
        return orgaos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar Órgãos: {e}")

# Soft ou Hard delete
@router.delete("/delete/{id_orgao}")
def remover_orgao(
    id_orgao: int = Path(..., description="ID do Órgão a ser removido"),
    soft: bool = Query(False, description="Se 'true', faz soft delete (ativo=0).")
    , session: Session = Depends(get_session)
):
    orgao = session.get(Orgao, id_orgao)
    if not orgao:
        raise HTTPException(status_code=404, detail="Órgão não encontrado.")

    if soft:
        if not orgao.ativo:
            raise HTTPException(status_code=400, detail="Órgão já está inativo.")
        orgao.ativo = False
        add_to_log(
            db=session,
            tipo_operacao=TipoOperacao.INATIVACAO,
            entidade_alvo=EntidadeAlvo.ORGAO,
            operation=f"[DELETE] O Órgão {orgao.nome} foi inativado(a)",
        )  
    else:
        session.delete(orgao)
        add_to_log(
            db=session,
            tipo_operacao=TipoOperacao.REMOCAO,
            entidade_alvo=EntidadeAlvo.ORGAO,
            operation=f"[DELETE] O Órgão {orgao.nome} foi deletado(a)",
        )  

    session.commit()
    return {
        "status": "success",
        "message": "Órgão inativado (soft delete)." if soft else "Órgão removido permanentemente."
    }

# Reativar
@router.put("/reativar/{id_orgao}")
def reativar_orgao(id_orgao: int, session: Session = Depends(get_session)):
    orgao = session.get(Orgao, id_orgao)
    if not orgao:
        raise HTTPException(status_code=404, detail="Órgão não encontrado.")
    if orgao.ativo:
        raise HTTPException(status_code=400, detail="Órgão já está ativo.")

    orgao.ativo = True
    session.commit()
    session.refresh(orgao)
    add_to_log(
        db=session,
        tipo_operacao=TipoOperacao.REATIVACAO,
        entidade_alvo=EntidadeAlvo.ORGAO,
        operation=f"[REACTIVATE] O Órgão {orgao.nome} foi reativado(a)",
    )  
    return {"status": "success", "message": "Órgão reativado com sucesso."}