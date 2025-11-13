from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlmodel import Session, select, and_
from typing import List, Optional
from utils.history_log import add_to_log
from models import Ocupacao, Cargo, Orgao, Pessoa
from database import get_session

router = APIRouter(prefix="/api/ocupacao", tags=["Ocupação"])

# Criar ocupação
@router.post("/")
def adicionar_ocupacao(ocupacao: Ocupacao, session: Session = Depends(get_session)):
    try:
        # === Regra 0: data_inicio não pode ser posterior a data_fim ===
        if ocupacao.data_inicio and ocupacao.data_fim:
            if ocupacao.data_inicio > ocupacao.data_fim:
                raise HTTPException(
                    status_code=400,
                    detail="A data de início não pode ser posterior à data de fim."
                )

        # === Regra 1: impedir ocupação de cargo exclusivo com sobreposição ===
        cargo = session.get(Cargo, ocupacao.id_cargo)
        if cargo and cargo.exclusivo:
            data_inicio_nova = ocupacao.data_inicio or date.min
            data_fim_nova = ocupacao.data_fim or date(9999, 12, 31)

            ocupacao_existente = session.exec(
                select(Ocupacao)
                .where(
                    and_(
                        Ocupacao.id_cargo == ocupacao.id_cargo,
                        (Ocupacao.data_inicio <= data_fim_nova),
                        ((Ocupacao.data_fim == None) | (Ocupacao.data_fim >= data_inicio_nova))
                    )
                )
            ).first()

            if ocupacao_existente:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"O cargo {ocupacao.id_cargo} já está ocupado "
                        f"pela pessoa {ocupacao_existente.id_pessoa}."
                    )
                )

        # === Regra 2: impedir 3ª ocupação consecutiva da mesma pessoa ===
        ultimas = session.exec(
            select(Ocupacao.id_pessoa)
            .where(Ocupacao.id_cargo == ocupacao.id_cargo)
            .order_by(Ocupacao.data_fim.desc().nulls_last())
            .limit(2)
        ).all()

        if len(ultimas) == 2 and all(pid == ocupacao.id_pessoa for pid in ultimas):
            raise HTTPException(
                status_code=400,
                detail="As últimas duas ocupações deste cargo já foram dessa mesma pessoa."
            )

        # === Inserção da nova ocupação ===
        session.add(ocupacao)
        session.commit()
        session.refresh(ocupacao)

        pessoa = session.get(Pessoa, ocupacao.id_pessoa)
        orgao = session.get(Orgao, cargo.id_orgao)
        add_to_log(
            db=session,
            operation=f"[ADD] Adicionada ocupação ID {ocupacao.id_ocupacao} para {pessoa.nome} no cargo de {cargo.nome}, no órgão {orgao.nome}." 
        )
        
        return {
            "status": "success",
            "message": "Ocupação adicionada com sucesso",
            "id_ocupacao": ocupacao.id_ocupacao,
        }

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao adicionar Ocupação. Verifique se os IDs de Pessoa, Cargo e Portaria existem: {e}"
        )

# Listar ocupações
@router.get("/", response_model=List[Ocupacao])
def carregar_ocupacao(session: Session = Depends(get_session)):
    try:
        return session.exec(select(Ocupacao)).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar Ocupações: {e}")

# Remover ocupação
@router.delete("/delete/{id_ocupacao}")
def remover_ocupacao(id_ocupacao: int = Path(..., description="ID da Ocupação a ser removida"),
                     session: Session = Depends(get_session)):
    ocupacao = session.get(Ocupacao, id_ocupacao)
    if not ocupacao:
        raise HTTPException(status_code=404, detail="Ocupação não encontrada.")

    session.delete(ocupacao)
    session.commit()

    pessoa = session.get(Pessoa, ocupacao.id_pessoa)
    cargo = session.get(Cargo, ocupacao.id_cargo)
    orgao = session.get(Orgao, cargo.id_orgao)

    add_to_log(
        db=session,
        operation=f"[DELETE] Removida a ocupação de ID {ocupacao.id_ocupacao} para {pessoa.nome} no cargo de {cargo.nome}, no órgão {orgao.nome}." 
    )

    return {"status": "success", "message": "Ocupação removida com sucesso."}

# Finalizar ocupação
@router.put("/finalizar/{id_ocupacao}")
def finalizar_ocupacao(id_ocupacao: int = Path(..., description="ID da Ocupação a ser finalizada"),
                       session: Session = Depends(get_session)):
    ocupacao = session.get(Ocupacao, id_ocupacao)
    if not ocupacao:
        raise HTTPException(status_code=404, detail="Ocupação não encontrada.")

    if ocupacao.data_fim:
        raise HTTPException(status_code=400, detail="Essa ocupação já está finalizada.")

    ocupacao.data_fim = date.today()
    session.commit()
    session.refresh(ocupacao)

    pessoa = session.get(Pessoa, ocupacao.id_pessoa)
    cargo = session.get(Cargo, ocupacao.id_cargo)
    orgao = session.get(Orgao, cargo.id_orgao)

    add_to_log(
        db=session,
        operation=f"[END] Finalizada a ocupação de ID {ocupacao.id_ocupacao} para {pessoa.nome} no cargo de {cargo.nome}, no órgão {orgao.nome}." 
    )

    return {"status": "success", "message": "Ocupação finalizada com sucesso."}
