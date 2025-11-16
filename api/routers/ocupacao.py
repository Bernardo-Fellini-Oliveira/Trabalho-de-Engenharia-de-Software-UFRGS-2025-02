from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, Session, nulls_first, or_, select, and_
from typing import List, Optional
from models.cargo import Cargo 
from models.ocupacao import Ocupacao
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
    
    except IntegrityError as e:
        session.rollback()
        # checa se foi violação de unicidade
        error_code = getattr(e.orig, "pgcode", None)

        if error_code == '23505':  # código de erro para violação de unicidade no PostgreSQL
            raise HTTPException(
                status_code=409,
                detail="Já existe Ocupação com esses dados."
            )
        # outros erros de integridade
        raise HTTPException(400, f"Erro de integridade: {e}")

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


@router.delete("/delete_list/")
def remover_ocupacoes(id_ocupacoes: List[int],
                        session: Session = Depends(get_session)):
    try:
        ocupacoes = session.exec(select(Ocupacao).where(Ocupacao.id_ocupacao.in_(id_ocupacoes))).all()
        if not ocupacoes:
            raise HTTPException(status_code=404, detail="Nenhuma Ocupação encontrada para os IDs fornecidos.")

        for ocupacao in ocupacoes:
            session.delete(ocupacao)
        session.commit()

        return {"status": "success", "message": f"{len(ocupacoes)} Ocupações removidas com sucesso."}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao remover Ocupações: {e}")




class FinalizarOcupacaoRequest(SQLModel):
    definitiva: bool
    data_fim: date
    data_inicio_substitutos: Optional[date] = None
    data_fim_substitutos: Optional[date] = None


    

@router.put("/finalizar/{id_ocupacao}")
def finalizar_ocupacao(
    id_ocupacao: int,
    payload: FinalizarOcupacaoRequest,
    session: Session = Depends(get_session)
):

    # ------------------------------------------
    # 1. Buscar ocupação e cargo atual
    # ------------------------------------------
    ocupacao = session.get(Ocupacao, id_ocupacao)
    if not ocupacao:
        raise HTTPException(404, "Ocupação não encontrada.")

    ocupacao.data_fim = payload.data_fim
    cargo_atual = session.get(Cargo, ocupacao.id_cargo)

    if not cargo_atual:
        raise HTTPException(500, "Cargo associado à ocupação não existe (!).")

    if(cargo_atual.ativo == False):
        raise HTTPException(400, "O cargo associado à ocupação está inativo.")
    
    if(cargo_atual.substituto is None and not payload.definitiva):
        raise HTTPException(400, "Não é possível fazer substituição automática: o cargo não possui substituto.")
    
    # ------------------------------------------
    # 2. Obter cadeia completa (para baixo)
    # ------------------------------------------
    cadeia = []
    atual = cargo_atual

    while atual is not None:
        print("===========================")
        print(f"Adicionando cargo {atual.id_cargo} à cadeia.")
        print("===========================")
        cadeia.append(atual)
        atual = session.get(Cargo, atual.substituto) if atual.substituto else None

    # Cadeia = [A, B, C, D]   (A é o titular)

    # ------------------------------------------
    # 3. Finalizar todas as ocupações vigentes da cadeia
    # ------------------------------------------
    ocupacoes = [ocupacao]

    for cargo in cadeia[1:]:
        query = (
            select(Ocupacao)
            .where(Ocupacao.id_cargo == cargo.id_cargo)
            .where(
                # data_inicio <= data_ref  OU  inicio NULL
                or_(
                    Ocupacao.data_inicio <= payload.data_fim,
                    Ocupacao.data_inicio == None
                )
            )
            .where(
                # data_fim >= data_ref  OU  fim NULL
                or_(
                    Ocupacao.data_fim == None,
                    Ocupacao.data_fim >= payload.data_fim
                )
            )

            # ORDER BY NULLS FIRST
            .order_by(
                nulls_first(Ocupacao.data_fim.desc()),
                nulls_first(Ocupacao.data_inicio.desc())
            )
            
        )


        oc = session.exec(query).first()

        if oc:
            print("===========================")
            print(f"Ocupação vigente para cargo {cargo.id_cargo} encontrada: {oc.id_ocupacao}")
            print("===========================")
            oc.data_fim = payload.data_fim
            ocupacoes.append(oc)

    session.flush()

    # ------------------------------------------
    # CASO 1 — FINALIZAÇÃO DEFINITIVA
    # ------------------------------------------
    if payload.definitiva:
        session.commit()
        return {
            "status": "success",
            "message": "Ocupação finalizada definitivamente e cadeia encerrada.",
            "ids": [c.id_cargo for c in cadeia]
        }

    # ------------------------------------------
    # CASO 2 — SUBSTITUIÇÃO AUTOMÁTICA
    # ------------------------------------------

    if len(ocupacoes) < 2:
        raise HTTPException(400, "Não há substitutos na cadeia para assumir a ocupação.")

    
    data_inicio = payload.data_inicio_substitutos or payload.data_fim
    data_fim_nova = payload.data_fim_substitutos

    # cadeia = [A, B, C, D]
    # criar novas ocupações:
    #   B assume A
    #   C assume B
    #   D assume C
    novos_ids = []

    for i in range(1, len(ocupacoes)):
        print("===========================")
        print(len(ocupacoes))
        print(i)
        print("===========================")

        acima = ocupacoes[i - 1]
        atual = ocupacoes[i]

        nova = Ocupacao(
            id_pessoa = atual.id_pessoa,
            id_cargo = acima.id_cargo,
            data_inicio = data_inicio,
            data_fim = data_fim_nova,
            mandato = 1,
            observacoes = "Substituição automática"
        )

        session.add(nova)
        novos_ids.append(nova.id_ocupacao)

    session.commit()

    return {
        "status": "success",
        "message": "Ocupação finalizada e substitutos assumiram automaticamente.",
        "ids": novos_ids
    }
