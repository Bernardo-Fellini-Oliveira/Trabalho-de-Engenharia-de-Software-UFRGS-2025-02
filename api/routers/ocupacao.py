from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, Session, nulls_first, or_, select, and_
from typing import List, Optional, Set

from models.notificacoes import Notificacoes
from utils.history_log import add_to_log
from utils.enums import EntidadeAlvo, TipoOperacao
from models.cargo import Cargo 
from models.ocupacao import Ocupacao
from models.orgao import Orgao
from models.pessoa import Pessoa
from database import get_session

class FinalizarOcupacaoRequest(SQLModel):
    definitiva: bool
    data_fim: date
    data_inicio_substitutos: Optional[date] = None
    data_fim_substitutos: Optional[date] = None
    
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
        # Carregar objetos para logs e notificações
        cargo = session.get(Cargo, ocupacao.id_cargo)
        pessoa = session.get(Pessoa, ocupacao.id_pessoa)

        # === Regra 0: data_inicio não pode ser posterior a data_fim ===
        if ocupacao.data_inicio and ocupacao.data_fim:
            if ocupacao.data_inicio > ocupacao.data_fim:
                raise HTTPException(
                    status_code=400,
                    detail="A data de início não pode ser posterior à data de fim."
                )
            
        # === Regra 1: impedir ocupação de cargo exclusivo com sobreposição ===
        # cargo já carregado acima
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
                dadospayload = ocupacao.model_dump()
                cargo = session.get(Cargo, ocupacao.id_cargo)
                orgao = session.get(Orgao, cargo.id_orgao)
                pessoa = session.get(Pessoa, ocupacao_existente.id_pessoa)
                solicitacao = Notificacoes(
                    operation=f"O cargo {cargo.nome}, do órgão {orgao.nome}, já está ocupado por {pessoa.nome}. Abrindo solicitação de aprovação para esta ocupação.",
                    tipo_operacao=TipoOperacao.ASSOCIACAO,
                    entidade_alvo=EntidadeAlvo.OCUPACAO,
                    dados_payload=dadospayload,
                    id_afetado=ocupacao_existente.id_ocupacao,
                    regra=1   
                )
                session.add(solicitacao)
                session.commit()
                session.refresh(solicitacao)

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"O cargo {cargo.nome}, do órgão {orgao.nome}, já está ocupado por {pessoa.nome}. Abrindo solicitação de aprovação para esta ocupação."
                    )
                )

        # === Regra 2: impedir 3ª ocupação consecutiva da mesma pessoa ===

        """
        if len(ultimas) >= 2 and all(pid == ocupacao.id_pessoa for pid in ultimas) and cargo and cargo.exclusivo:
            dadospayload = ocupacao.model_dump()
            solicitacao = Notificacoes(
                operation=f"As últimas duas ou mais ocupações do cargo {cargo.nome} já foram de {pessoa.nome}. Criada uma solicitação de aprovação para esta ocupação.",
                tipo_operacao=TipoOperacao.ASSOCIACAO,
                entidade_alvo=EntidadeAlvo.OCUPACAO,
                dados_payload=dadospayload,
                regra=2   
            )
        """
        previous_ocupation = _get_prev_occupacao(session, ocupacao.id_cargo, ocupacao.data_inicio or date.min)
        next_ocupation = _get_next_occupacao(session, ocupacao.id_cargo, ocupacao.data_inicio or date.min)

        num_mandatos_seguidos = 1
        if previous_ocupation and previous_ocupation.id_pessoa == ocupacao.id_pessoa:
            num_mandatos_seguidos = (previous_ocupation.mandato or 0) + 1
        
        contador = num_mandatos_seguidos
        atual = next_ocupation
        
        # Simula a contagem futura
        while atual and atual.id_pessoa == ocupacao.id_pessoa:
            contador += 1
            atual = _get_next_occupacao(session, atual.id_cargo, atual.data_inicio or date.min, atual.id_ocupacao)

        if contador > 2:
            # Se ultrapassar 2 mandatos, cria notificação em vez de apenas bloquear
            session.rollback()
            try:
                dadospayload = ocupacao.model_dump(mode='json')
                
                solicitacao = Notificacoes(
                    operation=f"As últimas duas ocupações do cargo {cargo.nome} já foram de {pessoa.nome}. Criada uma solicitação de aprovação para esta ocupação.",
                    tipo_operacao=TipoOperacao.ASSOCIACAO,
                    entidade_alvo=EntidadeAlvo.OCUPACAO,
                    dados_payload=dadospayload,
                    regra=2   
                )

                session.add(solicitacao)
                session.commit()
                session.refresh(solicitacao)
            except Exception as e:
                session.rollback()
                raise HTTPException(status_code=500, detail=f"Erro interno ao criar notificação: {str(e)}")

            raise HTTPException(
                status_code=400,
                detail="As últimas duas ocupações do cargo já foram dessa mesma pessoa. Criada uma solicitação de aprovação para esta ocupação."
            )
        
        # Se não ultrapassou, aplica a atualização dos mandatos seguintes
        atual = next_ocupation
        contador_update = num_mandatos_seguidos
        while atual and atual.id_pessoa == ocupacao.id_pessoa:
            atual.mandato = contador_update + 1
            contador_update += 1
            session.add(atual) # Garante update na sessão
            # session.flush() # Removido flush excessivo, o commit final resolve
            atual = _get_next_occupacao(session, atual.id_cargo, atual.data_inicio or date.min, atual.id_ocupacao)
        
        # Checa pela quebra de uma sequência de mandatos
        if previous_ocupation and next_ocupation and previous_ocupation.id_pessoa == next_ocupation.id_pessoa != ocupacao.id_pessoa:
            next_ocupation.mandato = next_ocupation.mandato - 1
            session.add(next_ocupation) # Garante update

            
        nova_ocupacao = Ocupacao(
            id_pessoa=ocupacao.id_pessoa,
            id_cargo=ocupacao.id_cargo,
            id_portaria=ocupacao.id_portaria,
            data_inicio=ocupacao.data_inicio,
            data_fim=ocupacao.data_fim,
            mandato=num_mandatos_seguidos,
            observacoes=ocupacao.observacoes,
        )

        # Regra 3: Se o cargo é substituto de outro, deve existir uma ocupação com o cargo principal
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


def core_adicionar_ocupacoes_lote(
    ocupacoes: List[Ocupacao],
    session: Session
) -> List[dict]:
    resultados = []
    for ocupacao in ocupacoes:
        try:
            nova_ocupacao = core_adicionar_ocupacao(ocupacao, session)
            resultados.append({
                "status": "success",
                "message": "Ocupação adicionada com sucesso",
                "id_ocupacao": nova_ocupacao.id_ocupacao
            })
        except HTTPException as he:
            resultados.append({
                "status": "error",
                "detail": he.detail
            })
    return resultados

def _get_chain_below_ocupacoes(session: Session, ocupacao_base: Ocupacao) -> Set[int]:
    """
    Retorna o conjunto (set) de IDs de Ocupações que estão na cadeia de substituição
    abaixo da ocupação base. NÃO inclui a ocupação base.
    """
    ids_ocupacoes_substitutas = set()
    
    # 1. Obter o cargo que a ocupação base está ocupando
    cargo_pai = session.get(Cargo, ocupacao_base.id_cargo)

    # 2. Iniciar a busca pelo próximo cargo na cadeia de substituição de CARGOS
    cargo_atual_id = cargo_pai.substituto # Cargo que substitui o cargo pai
    
    # Define as datas de referência da ocupação superior
    data_inicio_base = ocupacao_base.data_inicio or date.min
    data_fim_base = ocupacao_base.data_fim or date(9999, 12, 31)

    # 3. Traversal Iterativo dos Cargos
    while cargo_atual_id is not None:
        
        cargo_substituto = session.get(Cargo, cargo_atual_id)
        if not cargo_substituto:
            break # Fim da cadeia ou erro
            
        # 4. Busca Ocupações Vigentes no CARGO SUBSTITUTO
        # A ocupação substituta deve ter seu período contido no período da ocupação base.
        stmt = (
            select(Ocupacao.id_ocupacao)
            .where(Ocupacao.id_cargo == cargo_atual_id)
            .where(
                # A ocupação substituta DEVE ter data de início >= data de início da base
                Ocupacao.data_inicio >= data_inicio_base
            )
            .where(
                or_(
                    # E data de fim <= data de fim da base
                    Ocupacao.data_fim <= data_fim_base,
                    # OU a base não tem data_fim (vigente) e o substituto não tem data_fim (vigente)
                    and_(ocupacao_base.data_fim == None, Ocupacao.data_fim == None)
                )
            )
            .order_by(Ocupacao.data_inicio.asc()) # Ordena para garantir lógica consistente
        )
        
        # Coleta todas as ocupações que se encaixam no período e no cargo
        ids_encontrados = session.exec(stmt).all()
        ids_ocupacoes_substitutas.update(ids_encontrados)
        
        # 5. Avança na Cadeia de Cargos
        cargo_atual_id = cargo_substituto.substituto # Próximo substituto na cadeia de CARGOS

    return ids_ocupacoes_substitutas


def reajustar_mandatos_com_remocao(session: Session, ocupacao_removida: Ocupacao):

    cargo = session.get(Cargo, ocupacao_removida.id_cargo)
    if not cargo.exclusivo:
        # Se o cargo não é exclusivo, não há necessidade de reajustar mandatos
        return
    
    # Busca vizinhos (após a remoção dos substitutos, se houver)
    previous_ocupation = _get_prev_occupacao(session, ocupacao_removida.id_cargo, ocupacao_removida.data_inicio or date.min, ocupacao_removida.id_ocupacao)
    next_ocupation = _get_next_occupacao(session, ocupacao_removida.id_cargo, ocupacao_removida.data_inicio or date.min, ocupacao_removida.id_ocupacao)

    # Identifica o PONTO DE MUDANÇA: Se a ocupação anterior e a próxima são da mesma pessoa.
    if previous_ocupation and next_ocupation and previous_ocupation.id_pessoa == next_ocupation.id_pessoa:
        
        # Sequência foi "fechada" após a remoção: Ajustar a numeração a partir de next_ocupation.
        atual = next_ocupation
        
        # O novo mandato do next_ocupation deve ser o mandato do previous_ocupation + 1
        contador = (previous_ocupation.mandato or 0) + 1 
        id_pessoa_mandato_afetado = atual.id_pessoa

        while atual and atual.id_pessoa == previous_ocupation.id_pessoa:
            atual.mandato = contador
            
            # Validação de limite (contador > 2)
            if contador > 2:
                # Lançamos a exceção ANTES do delete final, mas precisamos do rollback.
                raise HTTPException(
                    400,
                    f"Não é possível remover a ocupação: a pessoa {id_pessoa_mandato_afetado} ficaria com mais de 2 mandatos seguidos neste cargo."
                )

            session.add(atual) # Garante que a atualização está na sessão
            session.flush() # Persiste a mudança de mandato
            contador += 1
            
            # Próxima ocupação na sequência
            atual = _get_next_occupacao(session, atual.id_cargo, atual.data_inicio or date.min, atual.id_ocupacao)



def core_remover_ocupacao(
    id_ocupacao: int,
    session: Session
):
    # -----------------------------------------------------------------
    # 1. VALIDAÇÃO E CARREGAMENTO
    # -----------------------------------------------------------------
    ocupacao_removida = session.get(Ocupacao, id_ocupacao)
    if not ocupacao_removida:
        raise HTTPException(status_code=404, detail="Ocupação não encontrada.")
    
    # Carrega o cargo associado para checar a cadeia de substituição
    cargo_removido = session.get(Cargo, ocupacao_removida.id_cargo)
    if not cargo_removido:
         # Isso é um erro de integridade do BD, mas é bom checar
        raise HTTPException(500, "Cargo associado não encontrado.") 

    # -----------------------------------------------------------------
    # 2. REMOÇÃO EM CASCATA DA CADEIA DE SUBSTITUIÇÃO (NOVO!)
    # -----------------------------------------------------------------
    
    ids_ocupacoes_cadeia_abaixo = set()
    
    # Verifica se esta ocupação tem substitutos (i.e., se o Cargo dela é um substituto_para de outra ocupação)
    if cargo_removido.substituto is not None:
        
        # 2a. Coleta todas as ocupações na cadeia abaixo (substitutos diretos e subsequentes)
        # Esta é a função CRÍTICA: deve retornar as IDs das Ocupações que dependem dela.
        ids_ocupacoes_cadeia_abaixo = _get_chain_below_ocupacoes(session, ocupacao_removida)

        # 2b. Deleta as ocupações da cadeia abaixo (do final para o início, por segurança)
        for oid in ids_ocupacoes_cadeia_abaixo:
            ocupacao_a_deletar = session.get(Ocupacao, oid)
            if ocupacao_a_deletar:
                try:
                    reajustar_mandatos_com_remocao(session, ocupacao_a_deletar)
                except HTTPException:
                    raise
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Erro ao reajustar mandatos: {e}")
                
                session.delete(ocupacao_a_deletar)

    
        session.flush() # Persiste os DELETES dos substitutos

    # -----------------------------------------------------------------
    # 3. REAJUSTE DE MANDATOS
    # -----------------------------------------------------------------

    try:
        reajustar_mandatos_com_remocao(session, ocupacao_removida)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao reajustar mandatos: {e}")

    # -----------------------------------------------------------------
    # 4. REMOÇÃO FINAL DA OCUPAÇÃO-BASE
    # -----------------------------------------------------------------
    session.delete(ocupacao_removida)

    return {"status": "success", "message": "Ocupação removida e cadeia ajustada com sucesso.", "ids_removidos": list(ids_ocupacoes_cadeia_abaixo) + [id_ocupacao]}



# Criar ocupação
@router.post("/")
def adicionar_ocupacao(ocupacao: Ocupacao, session: Session = Depends(get_session)):
    try:
        nova_ocupacao = core_adicionar_ocupacao(ocupacao, session)
        
        # Adicionar Log
        cargo = session.get(Cargo, ocupacao.id_cargo)
        pessoa = session.get(Pessoa, ocupacao.id_pessoa)
        orgao = session.get(Orgao, cargo.id_orgao)
        
        add_to_log(
            session=session,
            tipo_operacao=TipoOperacao.ASSOCIACAO,
            entidade_alvo=EntidadeAlvo.OCUPACAO,
            operation=f"[ADD] Adicionada ocupação de {pessoa.nome} no cargo de {cargo.nome}, no órgão {orgao.nome}." 
        )
        
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
    
@router.post("/lote/")
def adicionar_ocupacoes_lote(ocupacoes: List[Ocupacao], session: Session = Depends(get_session)):
    try:
        resultados = core_adicionar_ocupacoes_lote(ocupacoes, session)
        session.commit()
        return {"results": resultados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar Ocupações em lote: {e}")


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
    
    try:
        # Busca dados para log antes de remover
        ocupacao = session.get(Ocupacao, id_ocupacao)
        if ocupacao:
            pessoa = session.get(Pessoa, ocupacao.id_pessoa)
            cargo = session.get(Cargo, ocupacao.id_cargo)
            orgao = session.get(Orgao, cargo.id_orgao)
            
            # Log
            add_to_log(
                session=session,
                tipo_operacao=TipoOperacao.REMOCAO,
                entidade_alvo=EntidadeAlvo.OCUPACAO,
                operation=f"[DELETE] Removida a ocupação de {pessoa.nome} no cargo de {cargo.nome}, no órgão {orgao.nome}." 
            )

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
            # Log
            pessoa = session.get(Pessoa, ocupacao.id_pessoa)
            cargo = session.get(Cargo, ocupacao.id_cargo)
            orgao = session.get(Orgao, cargo.id_orgao)
            add_to_log(
                session=session,
                tipo_operacao=TipoOperacao.REMOCAO,
                entidade_alvo=EntidadeAlvo.OCUPACAO,
                operation=f"[DELETE] Removida a ocupação de {pessoa.nome} no cargo de {cargo.nome}, no órgão {orgao.nome}." 
            )
            
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
    ocupacao_atualizada: Ocupacao, # Assume-se que esta é a nova representação completa do registro
    session: Session = Depends(get_session)
):
    try:
        ocupacao_antiga = session.get(Ocupacao, id_ocupacao)
        if not ocupacao_antiga:
            raise HTTPException(status_code=404, detail="Ocupação não encontrada.")
        
        # -------------------------------------------------------------
        # 1. VERIFICAÇÃO DE ALTO IMPACTO (datas E/OU cargo)
        # -------------------------------------------------------------
        
        # Verifica se houve alteração no ID do cargo, data de início ou data de fim.
        houve_alteracao_complexa = (
            ocupacao_atualizada.id_cargo != ocupacao_antiga.id_cargo or 
            ocupacao_atualizada.data_fim != ocupacao_antiga.data_fim or 
            ocupacao_atualizada.data_inicio != ocupacao_antiga.data_inicio or
            ocupacao_atualizada.id_pessoa != ocupacao_antiga.id_pessoa
        )
        
        # 2. SE HOUVE ALTERAÇÃO COMPLEXA, CHECAMOS POR SUBTITUTOS
        if houve_alteracao_complexa:
            
            # Coleta a cadeia de substitutos que dependem desta ocupação
            # NOTA: Usamos a ocupação antiga (occupacao_antiga) como base para a checagem
            ids_ocupacoes_cadeia_abaixo = _get_chain_below_ocupacoes(session, ocupacao_antiga)
            if ids_ocupacoes_cadeia_abaixo:
                # CONFLITO: Devolve a lista de IDs para o front-end resolver
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"Alteração de alto impacto inválida: {len(ids_ocupacoes_cadeia_abaixo)} substituto(s) na cadeia abaixo. "
                        "Remova-os, ou envie a confirmação/dados de reajuste."
                    ),
                    # Você pode usar headers ou um modelo de erro customizado para retornar os IDs
                    # Neste exemplo, eles estão na descrição do erro (detail).
                )
            
        # -------------------------------------------------------------
        # 3. SE NÃO HOUVE ALTERAÇÃO COMPLEXA, PROSSEGUIMOS SIMPLESMENTE ALTERANDO OS CAMPOS RESTANTES, 
        # O QUE É BEM MAIS EFICIENTE QUE A OPÇÃO DE REMOVER + ADICIONAR
        if not houve_alteracao_complexa:
            ocupacao_antiga.id_portaria = ocupacao_atualizada.id_portaria
            ocupacao_antiga.observacoes = ocupacao_atualizada.observacoes
            
            session.commit()
            session.refresh(ocupacao_antiga)
            
            return {
                "status": "success",
                "message": "Ocupação alterada com sucesso.",
                "id_ocupacao": ocupacao_antiga.id_ocupacao
            }

        # -------------------------------------------------------------
        # 4. NESSE CASO, HOUVE ALTERAÇÃO COMPLEXA, MAS NÃO HÁ SUBSTITUTOS
        # FAZEMOS ENTÃO UMA ALTERAÇÃO ATÔMICA (Remover Antiga + Adicionar Nova), 
        # POIS A ADIÇÃO E A REMOÇÃO JÁ ESTÃO CORRETAMENTE TRATANDO AS REGRAS DE NEGÓCIO
        
        # 4a. REMOVER A OCUPAÇÃO ANTIGA (Com toda a lógica de reajuste de mandatos nos vizinhos)
        core_remover_ocupacao(id_ocupacao, session)
        session.flush() # Persiste o DELETE e o UPDATE dos mandatos
        
        # 4b. ADICIONAR A NOVA OCUPAÇÃO
        # (O core_adicionar_ocupacao aplica as regras de exclusividade, 3 mandatos, etc.)
        ocupacao_persistida = core_adicionar_ocupacao(ocupacao_atualizada, session)
        
        # 4c. COMMIT ÚNICO (Atomicidade)
        session.commit()
        session.refresh(ocupacao_persistida)
        
        return {
            "status": "success",
            "message": "Ocupação atualizada com sucesso.",
            "id_ocupacao": ocupacao_persistida.id_ocupacao
        }
    
    except IntegrityError as e:
        session.rollback()
        # Tratamento para violações de chave única/foreign key
        error_code = getattr(e.orig, "pgcode", None)
        if error_code == '23505':
            raise HTTPException(409, "Nova ocupação viola restrição de unicidade.")
        if error_code == '23503':
            raise HTTPException(400, "ID de Cargo ou Pessoa inválido.")
        raise HTTPException(400, f"Erro de integridade: {e}")
    
    except HTTPException:
        session.rollback() # Garante rollback para 409, 400 ou 404
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao alterar Ocupação: {e}")




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
    
    pessoa = session.get(Pessoa, ocupacao.id_pessoa)
    cargo = session.get(Cargo, ocupacao.id_cargo)
    orgao = session.get(Orgao, cargo.id_orgao)

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
            oc.data_fim = payload.data_fim
            ocupacoes.append(oc)

    session.flush()

    # ------------------------------------------
    # CASO 1 — FINALIZAÇÃO DEFINITIVA
    # ------------------------------------------
    if payload.definitiva:
        add_to_log(
            session=session,
            tipo_operacao=TipoOperacao.FINALIZACAO,
            entidade_alvo=EntidadeAlvo.OCUPACAO,
            operation=f"[END] Finalizada ocupação de {pessoa.nome} no cargo de {cargo.nome}, no órgão {orgao.nome}."
        )
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
    
    add_to_log(
        session=session,
        tipo_operacao=TipoOperacao.FINALIZACAO,
        entidade_alvo=EntidadeAlvo.OCUPACAO,
        operation=f"[END] Finalizada ocupação de {pessoa.nome} no cargo de {cargo.nome}, no órgão {orgao.nome}. Substitutos assumiram."
    )

    session.commit()

    return {
        "status": "success",
        "message": "Ocupação finalizada e substitutos assumiram automaticamente.",
        "ids": novos_ids
    }