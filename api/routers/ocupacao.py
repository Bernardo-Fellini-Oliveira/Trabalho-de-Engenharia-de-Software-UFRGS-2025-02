from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlmodel import Session, select, and_
from typing import List, Optional
from models import Ocupacao, Cargo
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
            

            """

            SELECT id_ocupacao, id_pessoa 
            FROM Ocupacao JOIN Cargo ON Ocupacao.id_cargo = Cargo.id_cargo
            WHERE Cargo.exclusivo = 1 AND Ocupacao.id_cargo = %s AND 
            (
                -- Conflito: Ocupação existente (data_inicio) precede o NOVO FIM
                Ocupacao.data_inicio <= %s OR Ocupacao.data_inicio IS NULL 
                AND 
                -- E Ocupação existente (data_fim) sucede o NOVO INÍCIO
                (Ocupacao.data_fim IS NULL OR Ocupacao.data_fim >= %s)
            )
            ,
            # Parâmetros:
            (ocupacao.id_cargo, data_fim_novo, ocupacao.data_inicio) 

"""


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
                        ((Ocupacao.data_inicio <= data_fim_nova) | (Ocupacao.data_inicio == None)),
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
        ).all()

        if len(ultimas) >= 2 and all(pid == ocupacao.id_pessoa for pid in ultimas):
            raise HTTPException(
                status_code=400,
                detail="As últimas duas ocupações deste cargo já foram dessa mesma pessoa."
            )
        
        num_mandatos_seguidos = len(ultimas) + 1

        print(num_mandatos_seguidos)
        nova_ocupacao = Ocupacao(
            id_pessoa=ocupacao.id_pessoa,
            id_cargo=ocupacao.id_cargo,
            id_portaria=ocupacao.id_portaria,
            data_inicio=ocupacao.data_inicio,
            data_fim=ocupacao.data_fim,
            mandato=num_mandatos_seguidos
        )

        # === Inserção da nova ocupação ===
        session.add(nova_ocupacao)
        session.commit()
        session.refresh(nova_ocupacao)

        return {
            "status": "success",
            "message": "Ocupação adicionada com sucesso",
            "id_ocupacao": nova_ocupacao.id_ocupacao,
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

    return {"status": "success", "message": "Ocupação finalizada com sucesso."}
