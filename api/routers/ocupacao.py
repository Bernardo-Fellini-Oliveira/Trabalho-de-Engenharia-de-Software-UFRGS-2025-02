from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, Session, nulls_first, or_, select, and_
from typing import List, Optional
from models.cargo import Cargo 
from models.ocupacao import Ocupacao
from database import get_session

router = APIRouter(prefix="/api/ocupacao", tags=["Ocupação"])


def _get_prev_occupacao(session: Session, id_cargo: int, data_inicio, id_ocupacao: Optional[int] = None):
    """
    Ocupação imediatamente anterior ao ponto data_inicio.
    Se houver empates em data_inicio, usamos id_ocupacao como tie-breaker (maior id = mais recente).
    """
    stmt = (
        select(Ocupacao)
        .where(Ocupacao.id_cargo == id_cargo)
        .where(Ocupacao.data_inicio <= data_inicio)
        .where(Ocupacao.id_ocupacao != id_ocupacao if id_ocupacao is not None else True)
        .order_by(Ocupacao.data_inicio.desc(), Ocupacao.id_ocupacao.desc())
        .limit(1)
    )
    return session.exec(stmt).first()


def _get_next_occupacao(session: Session, id_cargo: int, data_inicio, id_ocupacao: Optional[int] = None):
    """
    Ocupação imediatamente posterior ao ponto data_inicio.
    """
    stmt = (
        select(Ocupacao)
        .where(Ocupacao.id_cargo == id_cargo)
        .where(Ocupacao.data_inicio >= data_inicio)
        .where(Ocupacao.id_ocupacao != id_ocupacao if id_ocupacao is not None else True)
        .order_by(Ocupacao.data_inicio.asc(), Ocupacao.id_ocupacao.asc())
        .limit(1)
    )
    return session.exec(stmt).first()



def core_adicionar_ocupacao(
    ocupacao: Ocupacao,
    session: Session
):
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
                        ((Ocupacao.data_inicio < data_fim_nova) | (Ocupacao.data_inicio == None)),
                        ((Ocupacao.data_fim == None) | (Ocupacao.data_fim > data_inicio_nova))
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

        previous_ocupation = _get_prev_occupacao(session, ocupacao.id_cargo, ocupacao.data_inicio or date.min)
        next_ocupation = _get_next_occupacao(session, ocupacao.id_cargo, ocupacao.data_inicio or date.min)

        num_mandatos_seguidos = 1
        if previous_ocupation and previous_ocupation.id_pessoa == ocupacao.id_pessoa:
            num_mandatos_seguidos = (previous_ocupation.mandato or 0) + 1
        
        contador = num_mandatos_seguidos
        atual = next_ocupation
        while atual and atual.id_pessoa == ocupacao.id_pessoa:
            atual.mandato = contador + 1
            contador += 1
            session.flush()
            atual = _get_next_occupacao(session, atual.id_cargo, atual.data_inicio or date.min, atual.id_ocupacao)
            print("ATUAL:", atual)


        if contador > 2:
            session.rollback()
            raise HTTPException(
                400,
                "Não é possível criar a ocupação: a pessoa já possui 2 mandatos seguidos neste cargo."
            )
        
        # Checa pela quebra de uma sequência de mandatos
        if previous_ocupation and next_ocupation and previous_ocupation.id_pessoa == next_ocupation.id_pessoa != ocupacao.id_pessoa:
            next_ocupation.mandato = next_ocupation.mandato - 1
            session.flush()

            
        nova_ocupacao = Ocupacao(
            id_pessoa=ocupacao.id_pessoa,
            id_cargo=ocupacao.id_cargo,
            id_portaria=ocupacao.id_portaria,
            data_inicio=ocupacao.data_inicio,
            data_fim=ocupacao.data_fim,
            mandato=num_mandatos_seguidos
        )

        # Regra 3: Se o cargo é substituto de outro, deve existir uma ocupação com o cargo principal com período de início anterior ou igual ao 
        # início da nova ocupação (ou nulo) e período de fim posterior ou igual ao início da nova ocupação (ou nulo)
        if cargo and cargo.substituto_para is not None:
            
            if nova_ocupacao.data_inicio is None:
                raise HTTPException(
                    400,
                    "Para cargos substitutos, é obrigatório informar a data de início."
                )

            data_ref = nova_ocupacao.data_inicio

            # Cargo principal
            cargo_principal = session.get(Cargo, cargo.substituto_para)
            if not cargo_principal:
                raise HTTPException(
                    500,
                    f"Cargo principal {cargo.substituto_para} não existe."
                )

            ocupacao_principal = session.exec(
                select(Ocupacao)
                .where(Ocupacao.id_cargo == cargo_principal.id_cargo)
                .where(
                    or_(
                        Ocupacao.data_inicio <= data_ref,
                        Ocupacao.data_inicio == None
                    )
                )
                .where(
                    or_(
                        Ocupacao.data_fim == None,
                        Ocupacao.data_fim >= data_ref
                    )
                )
            ).first()

            if not ocupacao_principal:
                raise HTTPException(
                    400,
                    (
                        f"Não é possível criar ocupação para o cargo substituto {cargo.id_cargo}: "
                        f"não existe ocupação vigente para o cargo principal {cargo_principal.id_cargo} "
                        f"na data {data_ref}."
                    )
                )

        # === Inserção da nova ocupação ===
        session.add(nova_ocupacao)

        return nova_ocupacao


# Criar ocupação
@router.post("/")
def adicionar_ocupacao(ocupacao: Ocupacao, session: Session = Depends(get_session)):
    try:
        nova_ocupacao = core_adicionar_ocupacao(ocupacao, session)
        session.commit()
        session.refresh(nova_ocupacao)

        
        return {
            "status": "success",
            "message": "Ocupação adicionada com sucesso",
            "id_ocupacao": nova_ocupacao.id_ocupacao
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


def core_remover_ocupacao(
    id_ocupacao: int,
    session: Session
):
    ocupacao_removida = session.get(Ocupacao, id_ocupacao)
    if not ocupacao_removida:
        raise HTTPException(status_code=404, detail="Ocupação não encontrada.")

    previous_ocupation = _get_prev_occupacao(session, ocupacao_removida.id_cargo, ocupacao_removida.data_inicio or date.min, ocupacao_removida.id_ocupacao)
    next_ocupation = _get_next_occupacao(session, ocupacao_removida.id_cargo, ocupacao_removida.data_inicio or date.min, ocupacao_removida.id_ocupacao)

    contador = 1
    # Checa se a pessoa da ocupação removida é a mesma da próxima -> quebrou a sequência
    if next_ocupation and ocupacao_removida.id_pessoa == next_ocupation.id_pessoa:
        
        # Inicia a iteração para reajustar a numeração
        atual = next_ocupation
        contador = ocupacao_removida.mandato 
        id_pessoa_mandato_afetado = atual.id_pessoa

        while atual and atual.id_pessoa == ocupacao_removida.id_pessoa:
            atual.mandato = contador
            contador += 1
            session.flush()
            atual = _get_next_occupacao(session, atual.id_cargo, atual.data_inicio or date.min, atual.id_ocupacao)


    # Checa se gerou uma sequência nova entre a anterior e a próxima
    elif previous_ocupation and next_ocupation and previous_ocupation.id_pessoa == next_ocupation.id_pessoa:
        id_pessoa_mandato_afetado = previous_ocupation.id_pessoa

        # Deve ir atualizando a numeração de mandatos a partir da próxima ocupaçã até quebrar a sequência
        atual = next_ocupation
        contador = previous_ocupation.mandato + 1
        while atual and atual.id_pessoa == previous_ocupation.id_pessoa:
            atual.mandato = contador
            session.flush()
            contador += 1
            atual = _get_next_occupacao(session, atual.id_cargo, atual.data_inicio or date.min, atual.id_ocupacao)

    if contador > 2:
        raise HTTPException(
            400,
            f"Não é possível remover a ocupação: a pessoa {id_pessoa_mandato_afetado} ficaria com mais de 2 mandatos seguidos neste cargo."
        )

    # Finalmente, remove a ocupação
    session.delete(ocupacao_removida)

    return {"status": "success", "message": "Ocupação removida com sucesso."}



# Remover ocupação
@router.delete("/delete/{id_ocupacao}")
def remover_ocupacao(id_ocupacao: int = Path(..., description="ID da Ocupação a ser removida"),
                     session: Session = Depends(get_session)):
    
    try:
        resultado = core_remover_ocupacao(id_ocupacao, session)
        session.commit()
        return resultado
    except HTTPException:
        session.rollback()
        raise 
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao remover Ocupação: {e}")


@router.delete("/delete_list/")
def remover_ocupacoes(id_ocupacoes: List[int],
                        session: Session = Depends(get_session)):
    try:
        ocupacoes = session.exec(select(Ocupacao).where(Ocupacao.id_ocupacao.in_(id_ocupacoes))).all()
        if not ocupacoes:
            raise HTTPException(status_code=404, detail="Nenhuma Ocupação encontrada para os IDs fornecidos.")

        for ocupacao in ocupacoes:
            core_remover_ocupacao(ocupacao.id_ocupacao, session)
        session.commit()

        return {"status": "success", "message": f"{len(ocupacoes)} Ocupações removidas com sucesso."}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao remover Ocupações: {e}")



@router.put("/alterar/{id_ocupacao}")
def alterar_ocupacao(
    id_ocupacao: int,
    ocupacao_atualizada: Ocupacao,
    session: Session = Depends(get_session)
):

    try:
        core_remover_ocupacao(id_ocupacao, session)
        session.flush()
        ocupacao_atualizada = core_adicionar_ocupacao(ocupacao_atualizada, session)
        session.commit()

        session.refresh(ocupacao_atualizada)

        print("OCUPACAO: ", ocupacao_atualizada)

        return {
            "status": "success",
            "message": "Ocupação atualizada com sucesso.",
            "id_ocupacao": ocupacao_atualizada.id_ocupacao
        }
    
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao alterar Ocupação: {e}")





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
