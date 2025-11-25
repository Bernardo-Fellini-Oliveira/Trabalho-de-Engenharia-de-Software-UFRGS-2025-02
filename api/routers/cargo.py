from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, Session, delete, select
from typing import List, Optional
from datetime import datetime

from utils.history_log import add_to_log
from models.cargo import Cargo
from models.orgao import Orgao
from models.ocupacao import Ocupacao
from utils.enums import TipoOperacao, EntidadeAlvo
from database import get_session


router = APIRouter(prefix="/api/cargo", tags=["Cargo"])


class CargoRead(SQLModel):
    id_cargo: int
    nome: str
    ativo: bool
    id_orgao: int
    exclusivo: bool
    substituto_para: Optional[int]
    substituto: Optional[int]
    created_at: datetime
    updated_at: datetime

class CargoCreate(SQLModel):
    nome: str
    ativo: bool = True
    id_orgao: int
    exclusivo: bool = True
    substituto_para: Optional[int] = None

class CargoUpdateData(SQLModel):
    nome: Optional[str] = None
    id_orgao: Optional[int] = None

def core_adicionar_cargo(
    cargo: CargoCreate,
    session: Session
) -> Cargo:

    # Criar objeto ORM novo cargo
    novo = Cargo(**cargo.model_dump())

    # ------------------------------------------
    # 1. Se não tem substituto_para, só cria direto
    # ------------------------------------------
    if novo.substituto_para is None:
        session.add(novo)
        session.flush() # Flush para gerar ID e validar constraints, commit é feito fora
        return novo
    
    else:
        if novo.exclusivo is False:
            raise HTTPException(
                400,
                "Cargos exclusivos não podem ser substitutos."
            )

    # ------------------------------------------
    # 2. Buscar o cargo que será substituído
    # ------------------------------------------
    acima = session.get(Cargo, novo.substituto_para)

    if acima is None:
        raise HTTPException(404, "Cargo 'substituto_para' não existe.")

    # Deve ser do mesmo órgão
    if acima.id_orgao != novo.id_orgao:
        raise HTTPException(
            400, "O substituto deve estar no mesmo órgão do cargo principal."
        )

    # ------------------------------------------
    # 3. O cargo acima já possui substituto?
    # ------------------------------------------
    if acima.substituto is not None:
        raise HTTPException(
            400,
            f"O cargo {acima.id_cargo} já possui um substituto definido."
        )

    # ------------------------------------------
    # 4. Verificação de ciclo
    # ------------------------------------------
    atual = acima
    while atual is not None:
        if atual.id_cargo == novo.id_cargo:
            raise HTTPException(
                400,
                "Ciclo detectado na cadeia de substituição."
            )
        atual = (
            session.get(Cargo, atual.substituto_para)
            if atual.substituto_para else None
        )

    # ------------------------------------------
    # 5. Criar o novo cargo como substituto
    # ------------------------------------------
    session.add(novo)
    session.flush()
    acima.substituto = novo.id_cargo

    update_stmt = (
                update(Cargo) 
                .where(Cargo.id_cargo == acima.id_cargo)
                .values(substituto=novo.id_cargo)
            )
    session.exec(update_stmt)

    return novo


def core_adicionar_cargos_lote(
    cargos: List[CargoCreate],
    session: Session
) -> List[Cargo]:
    resultados = []
    for cargo in cargos:
        try:
            novo = core_adicionar_cargo(cargo, session)
            # Log individual para lote é opcional, mas recomendado se o volume não for gigante
            orgao = session.get(Orgao, novo.id_orgao)
            add_to_log(
                session=session,
                tipo_operacao=TipoOperacao.ADICAO,
                entidade_alvo=EntidadeAlvo.CARGO,
                operation=f"[ADD] O cargo {novo.nome}, do órgão {orgao.nome}, foi adicionado(a)",
            )
            resultados.append({"status": "success", "cargo": novo})
        except HTTPException as he:
            resultados.append({"status": "error", "detail": he.detail})
    return resultados

def coletar_cadeia_abaixo(session: Session, cargo: Cargo, hard_delete: bool) -> List[Cargo]:
    """
    Retorna lista de cargos na cadeia *abaixo* do cargo (substitutos diretos e recursivos),
    na ordem imediata: [sub1, sub2, ...].
    """
    cadeia = []
    visitado = set()
    atual = cargo

    while atual and atual.substituto:
        proximo_id = atual.substituto
        if proximo_id in visitado:
            # proteção contra ciclo (não deveria ocorrer, mas por segurança)
            break
        visitado.add(proximo_id)
        proximo = session.get(Cargo, proximo_id)

        # Se a operação for um hard delete, vai preparando para deleção removendo a referência do substituto para não violar FK
        if hard_delete:
            atual.substituto = None

        if not proximo:
            break
        cadeia.append(proximo)
        atual = proximo

    return cadeia

def remover_cargo(
    id_cargo: int = Path(..., description="ID do Cargo a ser removido"),
    soft: bool = Query(False, description="Se 'true', realiza soft delete (ativo=0)."),
    force: bool = Query(False, description="Se 'true', ao fazer hard delete, também remove ocupações vinculadas."),
    session: Session = Depends(get_session),
    em_lote: bool = True
):
    cargo = session.get(Cargo, id_cargo)
    if not cargo:
        if em_lote:
            return {"status": "not_found", "message": f"Cargo não encontrado.", "ids": [id_cargo]}
        raise HTTPException(status_code=404, detail="Cargo não encontrado.")

    if not cargo.ativo and soft:
        if em_lote:
            return {"status": "already_inactive", "message": "Cargo já está inativo.", "ids": [id_cargo]}
        raise HTTPException(status_code=400, detail="Cargo já está inativo.")
    

    # busca o cargo acima (se houver) que aponta para este cargo
    acima = session.exec(select(Cargo).where(Cargo.substituto == cargo.id_cargo)).first()

    # coleta a cadeia abaixo (substitutos diretos/recursivos)
    cadeia_abaixo = coletar_cadeia_abaixo(session, cargo, hard_delete=not soft)
    session.flush()


    # cargos afetados: o próprio + toda a cadeia abaixo
    afetados = [cargo] + cadeia_abaixo

    ids_afetados = [c.id_cargo for c in afetados]


    if soft:
        # marca todos como inativos
        for c in afetados:
            if c.ativo:
                orgao = session.get(Orgao, c.id_orgao)
                c.ativo = False
                # Log para cada inativação
                add_to_log(
                    session=session,
                    tipo_operacao=TipoOperacao.REMOCAO,
                    entidade_alvo=EntidadeAlvo.CARGO,
                    operation=f"[DELETE/SOFT] O cargo {c.nome}, do órgão {orgao.nome}, foi inativado(a)"
                )

        # ajustar ponteiro do 'acima' para não apontar para cargo removido
        if acima:
            acima.substituto = None

        # commit automático ao sair do with
        return {"status": "success", "message": "Soft delete aplicado na cadeia.", "ids": ids_afetados}

    else:
        # HARD DELETE:
        # Verifica existências de ocupações (qualquer ocupação, histórica ou atual)
        stmt = select(Ocupacao).where(Ocupacao.id_cargo.in_(ids_afetados))
        ocup = session.exec(stmt).first()

        if ocup and not force:
            # há ocupações vinculadas e não permitimos apagar por padrão
            raise HTTPException(
                status_code=400,
                detail=(
                    "Existem ocupações vinculadas aos cargos afetados. "
                    "Use ?force=true para remover ocupações e cargos (operação destrutiva)."
                )
            )

        # se for force, remover ocupações vinculadas primeiro
        if ocup and force:
            # deletar todas ocupações que referenciam qualquer cargo da cadeia
            del_stmt = delete(Ocupacao).where(Ocupacao.id_cargo.in_(ids_afetados))
            session.exec(del_stmt)

        # atualizar ponteiro acima (se existir) para None
        if acima:
            acima.substituto = None
            session.add(acima)
            session.flush()


        # agora remover os cargos (do final para o início por segurança)
        # remover em ordem reversa evita FK problems (mas aqui substituto/substituto_para referenciam na mesma tabela)
        for c in reversed(afetados):
            orgao = session.get(Orgao, c.id_orgao)
            session.delete(c)
            
            # Log para cada deleção
            add_to_log(
                session=session,
                tipo_operacao=TipoOperacao.REMOCAO,
                entidade_alvo=EntidadeAlvo.CARGO,
                operation=f"[DELETE/HARD] O cargo {c.nome}, do órgão {orgao.nome}, foi deletado(a)"
            )
            session.flush()

        return {"status": "success", "message": "Hard delete realizado na cadeia.", "ids": ids_afetados}
    
def reativar_cargo(
    id_cargo: int = Path(..., description="ID do Cargo a ser reativado"),
    session: Session = Depends(get_session),
    em_lote: bool = True
):
    cargo = session.get(Cargo, id_cargo)

    if not cargo:
        if em_lote:
            return {"status": "not_found", "message": f"Cargo não encontrado.", "ids": [id_cargo]}
        raise HTTPException(status_code=404, detail="Cargo não encontrado.")
    if cargo.ativo:
        if em_lote:
            return {"status": "already_active", "message": "Cargo já está ativo.", "ids": [id_cargo]}
        raise HTTPException(status_code=400, detail="Cargo já está ativo.")
    
    afetados = [cargo.id_cargo]

    id_acima = cargo.substituto_para

    while id_acima:
        cargo_acima = session.get(Cargo, id_acima)
        if cargo_acima.ativo == False:
            cargo_acima.ativo = True
            afetados.append(cargo_acima.id_cargo)
            
            # Log para reativação recursiva
            orgao_acima = session.get(Orgao, cargo_acima.id_orgao)
            add_to_log(
                session=session,
                tipo_operacao=TipoOperacao.ALTERACAO, # Usando ALTERACAO pois REACTIVATE não estava no enum original
                entidade_alvo=EntidadeAlvo.CARGO,
                operation=f"[REACTIVATE] O cargo {cargo_acima.nome}, do órgão {orgao_acima.nome}, foi reativado(a)"
            )
            
            id_acima = cargo_acima.substituto_para
        else: 
            break


    cargo.ativo = True
    orgao = session.get(Orgao, cargo.id_orgao)
    add_to_log(
        session=session,
        tipo_operacao=TipoOperacao.ALTERACAO, 
        entidade_alvo=EntidadeAlvo.CARGO,
        operation=f"[REACTIVATE] O cargo {cargo.nome}, do órgão {orgao.nome}, foi reativado(a)"
    )
    
    return {"status": "success", "message": "Cargo reativado com sucesso.", "ids": afetados} 
def core_alterar_cargo(
    id_cargo: int,
    payload: CargoUpdateData,
    session: Session
):
    cargo = session.get(Cargo, id_cargo)
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo não encontrado.")
    
    novo_nome = payload.nome if payload.nome != cargo.nome else None
    novo_id_orgao = payload.id_orgao if payload.id_orgao != cargo.id_orgao else None

    # Verificar unicidade se houver mudança relevante - orgao nao deve conter cargo com mesmo nome
    if novo_nome is not None or novo_id_orgao is not None:

        nome_final = novo_nome if novo_nome is not None else cargo.nome
        orgao_final = novo_id_orgao if novo_id_orgao is not None else cargo.id_orgao

        # Consulta para achar outro cargo (diferente do atual) com a nova combinação
        stmt = (
            select(Cargo)
            .where(Cargo.nome == nome_final)
            .where(Cargo.id_orgao == orgao_final)
            .where(Cargo.id_cargo != cargo.id_cargo)
        )
        
        cargo_existente = session.exec(stmt).first()
        
        if cargo_existente:
            raise HTTPException(
                status_code=409,
                detail="Já existe um Cargo com esse nome nesse órgão."
            )

    # Aplica as mudanças
    if novo_nome is not None:
        cargo.nome = novo_nome
    if novo_id_orgao is not None:
        cargo.id_orgao = novo_id_orgao
    
    return cargo 

@router.post("/", response_model=CargoRead)
def adicionar_cargo(cargo: CargoCreate, session: Session = Depends(get_session)):

    try:
        novo = core_adicionar_cargo(cargo, session)
        
        # Adicionar Log
        orgao = session.get(Orgao, novo.id_orgao)
        add_to_log(
            session=session,
            tipo_operacao=TipoOperacao.ADICAO,
            entidade_alvo=EntidadeAlvo.CARGO,
            operation=f"[ADD] O cargo {novo.nome}, do órgão {orgao.nome}, foi adicionado(a)",
        ) 
        
        session.commit()
        session.refresh(novo)
        return CargoRead.model_validate(novo)

    except IntegrityError as e:
        session.rollback()
        error_code = getattr(e.orig, "pgcode", None)
        if error_code == "23505":
            raise HTTPException(
                409,
                "Já existe Cargo com esse nome para o órgão."
            )
        raise HTTPException(400, f"Erro de integridade: {e}")

    except Exception as e:
        session.rollback()
        raise HTTPException(500, f"Erro ao adicionar Cargo: {e}")


@router.post("/lote/")
def adicionar_cargos_lote(cargos: List[CargoCreate], session: Session = Depends(get_session)):
    try:
        resultados = core_adicionar_cargos_lote(cargos, session)
        session.commit()
        return {"results": resultados}

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar Cargos em lote: {e}")


@router.get("/", response_model=List[dict])
def carregar_cargo(session: Session = Depends(get_session)):
    try:
        dados = session.exec(select(Cargo, Orgao.nome).join(Orgao, Cargo.id_orgao == Orgao.id_orgao)).all()

        # Monta o retorno com o nome do órgão
        return [
            {
                "id_cargo": cargo.id_cargo,
                "nome": cargo.nome,
                "orgao": nome_orgao,
                "ativo": cargo.ativo,
                "exclusivo": cargo.exclusivo,
                "id_orgao": cargo.id_orgao,
                "substituto_para": cargo.substituto_para,
                'substituto': cargo.substituto
            }
            for (cargo, nome_orgao) in dados
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar Cargos: {e}")


@router.delete("/delete/{id_cargo}")
def remover_cargo_and_commit(
    id_cargo: int = Path(..., description="ID do Cargo a ser removido"),
    soft: bool = Query(False, description="Se 'true', realiza soft delete (ativo=0)."),
    force: bool = Query(False, description="Se 'true', ao fazer hard delete, também remove ocupações vinculadas."),
    session: Session = Depends(get_session)
):

    try:
        resultado = remover_cargo(id_cargo=id_cargo, soft=soft, force=force, session=session, em_lote=False)
        session.commit()

        return resultado

    except HTTPException:
        # repropaga erros de validação
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao remover/inativar cadeia: {e}")

@router.delete("/delete/lista/")
def remover_cargos_em_lote(
    ids_cargo: List[int] = Query(..., description="Lista de IDs de Cargos a serem removidos"),
    soft: bool = Query(False, description="Se 'true', realiza soft delete (ativo=0)."),
    force: bool = Query(False, description="Se 'true', ao fazer hard delete, também remove ocupações vinculadas."),
    session: Session = Depends(get_session)
):
    resultados = []
    try:
        for id_cargo in ids_cargo:
            resultado = remover_cargo(id_cargo=id_cargo, soft=soft, force=force, session=session, em_lote=True)
            resultados.append(resultado)

        session.commit()
        return resultados

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao processar remoção/inativação em lote: {e}")
    





# Reativar
@router.put("/reativar/{id_cargo}")
def reativar_cargo_and_commit(
    id_cargo: int = Path(..., description="ID do Cargo a ser reativado"),
    session: Session = Depends(get_session)
):

    resultado = reativar_cargo(id_cargo=id_cargo, session=session, em_lote=False)
    session.commit()
    return resultado

@router.put("/reativar/lista/")
def reativar_cargos_em_lote(
    ids_cargo: List[int] = Query(..., description="Lista de IDs de Cargos a serem reativados"),
    session: Session = Depends(get_session)
):
    resultados = []
    try:
        for id_cargo in ids_cargo:
            resultado = reativar_cargo(id_cargo=id_cargo, session=session, em_lote=True)
            resultados.append(resultado)

        session.commit()
        return resultados

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao processar reativação em lote: {e}")
    









@router.put("/{id_cargo}", response_model=CargoRead)
def alterar_cargo(
    id_cargo: int,
    payload: CargoUpdateData,
    session: Session = Depends(get_session)
):
    try:
        # A função core faz a validação de unicidade e aplica as alterações no objeto.
        cargo_atualizado = core_alterar_cargo(id_cargo, payload, session)
        
        # Log de alteração
        add_to_log(
            session=session,
            tipo_operacao=TipoOperacao.ALTERACAO,
            entidade_alvo=EntidadeAlvo.CARGO,
            operation=f"[UPDATE] O cargo {cargo_atualizado.nome} (ID: {id_cargo}) foi atualizado."
        )

        # A transação finaliza aqui, persistindo o UPDATE no objeto 'cargo_atualizado'.
        session.commit()
        session.refresh(cargo_atualizado)
        
        return cargo_atualizado
    
    except IntegrityError as e:
        session.rollback()
        # Tratamento para outras violações de integridade (ex: Foreign Key em id_orgao)
        error_code = getattr(e.orig, "pgcode", None)
        if error_code == '23503': # Código para Foreign Key Violation
            raise HTTPException(400, "O id_orgao especificado não existe.")
        
        raise HTTPException(400, f"Erro de integridade no banco de dados: {e}")
        
    except HTTPException:
        # Garante o rollback para erros de unicidade (código 409) ou not found (404) vindos do core
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(500, f"Erro interno ao atualizar cargo: {e}")