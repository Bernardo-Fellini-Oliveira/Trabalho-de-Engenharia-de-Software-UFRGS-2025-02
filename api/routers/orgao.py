from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from models.orgao import Orgao
from database import get_session

router = APIRouter(prefix="/api/orgao", tags=["Órgão"])


# Criar órgão
@router.post("/")
def adicionar_orgao(orgao: Orgao, session: Session = Depends(get_session)):
    try:
        session.add(orgao)
        session.commit()
        session.refresh(orgao)
        return {
            "status": "success",
            "message": "Órgão adicionado com sucesso",
            "id_orgao": orgao.id_orgao
        }
    
    except IntegrityError as e:
        session.rollback()
        # checa se foi violação de unicidade
        error_code = getattr(e.orig, "pgcode", None)

        if error_code == '23505':  # código de erro para violação de unicidade no PostgreSQL
            raise HTTPException(
                status_code=409,
                detail="Já existe Órgão com esse nome."
            )
        # outros erros de integridade
        raise HTTPException(400, f"Erro de integridade: {e}")
    
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


def remover_orgao(
    id_orgao: int,
    soft: bool,
    session: Session
):
    orgao = session.get(Orgao, id_orgao)
    if not orgao:
        raise HTTPException(status_code=404, detail="Órgão não encontrado.")

    if soft:
        if not orgao.ativo:
            raise HTTPException(status_code=400, detail="Órgão já está inativo.")
        orgao.ativo = False
    else:
        session.delete(orgao)

    return {
        "status": "success",
        "message": "Órgão inativado (soft delete)." if soft else "Órgão removido permanentemente."
    }


# Soft ou Hard delete
@router.delete("/delete/{id_orgao}")
def remover_orgao_endpoint(
    id_orgao: int = Path(..., description="ID do Órgão a ser removido"),
    soft: bool = Query(False, description="Se 'true', faz soft delete (ativo=0).")
    , session: Session = Depends(get_session)
):
    try:
        resultado = remover_orgao(id_orgao=id_orgao, soft=soft, session=session)
        session.commit()
        return resultado
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover Órgão: {e}")


@router.delete("/delete/lote/")
def remover_orgao_lote_endpoint(
    ids_orgaos: list[int] = Query(..., description="IDs dos Órgãos a serem removidos"),
    soft: bool = Query(False, description="Se 'true', faz soft delete (ativo=0)."),
    session: Session = Depends(get_session)
):
    resultados = []
    try:
        for id_orgao in ids_orgaos:
            try:
                resultado = remover_orgao(id_orgao=id_orgao, soft=soft, session=session)
                resultados.append({"id_orgao": id_orgao, "result": resultado})
            except HTTPException as he:
                resultados.append({"id_orgao": id_orgao, "error": he.detail})
        
        session.commit()
        return {"results": resultados}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover Órgãos em lote: {e}")
    


def reativar_orgao(
    id_orgao: int,
    session: Session
):
    orgao = session.get(Orgao, id_orgao)
    if not orgao:
        raise HTTPException(status_code=404, detail="Órgão não encontrado.")
    if orgao.ativo:
        raise HTTPException(status_code=400, detail="Órgão já está ativo.")

    orgao.ativo = True
    session.add(orgao)
    return {
        "status": "success",
        "message": "Órgão reativado com sucesso."
    }



# Reativar
@router.put("/reativar/{id_orgao}")
def reativar_orgao(id_orgao: int, session: Session = Depends(get_session)):

    try:
        retorno = reativar_orgao(id_orgao, session)
        session.commit()
        return retorno
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao reativar Órgão: {e}")
    
@router.put("/reativar/lote/")
def reativar_orgaos_em_lote(
    ids_orgaos: list[int] = Query(..., description="IDs dos Órgãos a serem reativados"),
    session: Session = Depends(get_session)
):
    resultados = []
    try:
        for id_orgao in ids_orgaos:
            try:
                resultado = reativar_orgao(id_orgao, session)
                resultados.append({"id_orgao": id_orgao, "result": resultado})
            except HTTPException as he:
                resultados.append({"id_orgao": id_orgao, "error": he.detail})
        
        session.commit()
        return {"results": resultados}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao reativar Órgãos em lote: {e}")

