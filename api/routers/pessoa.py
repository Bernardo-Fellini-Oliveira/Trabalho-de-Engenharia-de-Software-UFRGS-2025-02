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


def adicionar_pessoa(pessoa: Pessoa, session: Session = Depends(get_session)):
    if not pessoa.nome.strip():
        raise HTTPException(status_code=400, detail="O nome da pessoa não pode ser vazio.")
    
    pessoa.ativo = True  # força ativo=1 na criação
    session.add(pessoa)

    return {
        "status": "success",
        "message": "Pessoa adicionada com sucesso",
        "id_pessoa": pessoa.id_pessoa
    }

def adicionar_pessoa_lote(pessoas: list[Pessoa], session: Session = Depends(get_session)):
    resultados = []
    for pessoa in pessoas:
        try:
            resultado = adicionar_pessoa(pessoa, session)
            resultados.append({"pessoa": pessoa.nome, "result": resultado})
        except HTTPException as he:
            resultados.append({"pessoa": pessoa.nome, "error": he.detail})
    return resultados


# Criar pessoa
@router.post("/")
def adicionar_pessoa_endpoint(pessoa: Pessoa, session: Session = Depends(get_session)):
    try:
        retorno = adicionar_pessoa(pessoa, session)
        session.commit()
        session.refresh(pessoa)
        return retorno
    
    except IntegrityError as e:
        session.rollback()
        # checa se foi violação de unicidade
        error_code = getattr(e.orig, "pgcode", None)
        if error_code == '23505':  # código de erro para violação de unicidade no PostgreSQL
            raise HTTPException(
                status_code=409,
                detail="Já existe Pessoa com esse nome."
            )
        # outros erros de integridade
        raise HTTPException(400, f"Erro de integridade: {e}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar Pessoa: {e}")


def remover_pessoa(
    id_pessoa: int,
    soft: bool,
    session: Session
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

    return {
        "status": "success",
        "message": "Pessoa inativada (soft delete)." if soft else "Pessoa removida permanentemente."
    }



# Soft ou Hard delete
@router.delete("/delete/{id_pessoa}")
def remover_pessoa_endpoint(
    id_pessoa: int = Path(..., description="ID da Pessoa a ser removida"),
    soft: bool = Query(False, description="Se 'true', faz soft delete (ativo=0).")
    , session: Session = Depends(get_session)
):
    try:
        resultado = remover_pessoa(id_pessoa=id_pessoa, soft=soft, session=session)
        session.commit()
        return resultado
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover Pessoa: {str(e)}")


@router.delete("/delete/lote/")
def remover_pessoas_em_lote(
    ids_pessoas: list[int] = Query(..., description="IDs das Pessoas a serem removidas"),
    soft: bool = Query(False, description="Se 'true', faz soft delete (ativo=0)."),
    session: Session = Depends(get_session)
):
    resultados = []
    try:
        for id_pessoa in ids_pessoas:
            try:
                resultado = remover_pessoa(id_pessoa=id_pessoa, soft=soft, session=session)
                resultados.append({"id_pessoa": id_pessoa, "result": resultado})
            except HTTPException as he:
                resultados.append({"id_pessoa": id_pessoa, "error": he.detail})
        
        session.commit()
        return {"results": resultados}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover Pessoas em lote: {str(e)}")
    

def reativar_pessoa(
    id_pessoa: int,
    session: Session
):
    pessoa = session.get(Pessoa, id_pessoa)
    if not pessoa:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada.")
    if pessoa.ativo:
        raise HTTPException(status_code=400, detail="Pessoa já está ativa.")

    pessoa.ativo = True
    return {
        "status": "success",
        "message": "Pessoa reativada com sucesso."
    }

# Reativar pessoa
@router.put("/reativar/{id_pessoa}")
def reativar_pessoa_endpoint(id_pessoa: int, session: Session = Depends(get_session)):
    try:
        retorno = reativar_pessoa(id_pessoa, session)
        session.commit()
        return retorno

    except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao reativar Pessoa: {str(e)}")
    
@router.put("/reativar/lote/")
def reativar_pessoas_em_lote(
    ids_pessoas: list[int] = Query(..., description="IDs das Pessoas a serem reativadas"),
    session: Session = Depends(get_session)
):
    resultados = []
    try:
        for id_pessoa in ids_pessoas:
            try:
                resultado = reativar_pessoa(id_pessoa, session)
                resultados.append({"id_pessoa": id_pessoa, "result": resultado})
            except HTTPException as he:
                resultados.append({"id_pessoa": id_pessoa, "error": he.detail})
        
        session.commit()
        return {"results": resultados}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao reativar Pessoas em lote: {str(e)}")
    


# Atualizar pessoa
@router.put("/{id_pessoa}")
def atualizar_pessoa(
    id_pessoa: int = Path(..., description="ID da Pessoa a ser atualizada"),
    pessoa_atualizada: Pessoa = ...,
    session: Session = Depends(get_session)
):
    try:
        pessoa_existente = session.get(Pessoa, id_pessoa)
        if not pessoa_existente:
            raise HTTPException(status_code=404, detail="Pessoa não encontrada.")

        if not pessoa_atualizada.nome.strip():
            raise HTTPException(status_code=400, detail="O nome da pessoa não pode ser vazio.")

        pessoa_existente.nome = pessoa_atualizada.nome
        pessoa_existente.ativo = pessoa_atualizada.ativo

        session.add(pessoa_existente)
        session.commit()
        session.refresh(pessoa_existente)

        return {
            "status": "success",
            "message": "Pessoa atualizada com sucesso.",
            "id_pessoa": pessoa_existente.id_pessoa
        }

    except IntegrityError as e:
        session.rollback()
        # checa se foi violação de unicidade
        error_code = getattr(e.orig, "pgcode", None)
        if error_code == '23505':  # código de erro para violação de unicidade no PostgreSQL
            raise HTTPException(
                status_code=409,
                detail="Já existe Pessoa com esse nome."
            )
        # outros erros de integridade
        raise HTTPException(400, f"Erro de integridade: {e}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar Pessoa: {e}")
