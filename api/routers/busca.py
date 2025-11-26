from operator import itemgetter
from typing import Any, Callable, Dict, List, Tuple
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlmodel import Session, and_, func, or_, select
from models.orgao import Orgao
from models.cargo import Cargo 
from models.pessoa import Pessoa
from models.ocupacao import Ocupacao
from database import get_session
from collections import defaultdict
from search_grammar.parsers import parse_filtro, traduzir_parsing_result

router = APIRouter(
    prefix="/api",
    tags=["Busca"]
)


QUERY_BASE = {
    "pessoa": lambda: (
        select(
            Pessoa.nome, Cargo.nome, Orgao.nome,
            Ocupacao.data_inicio, Ocupacao.data_fim,
            Ocupacao.mandato, 
            Ocupacao.observacoes,
            Cargo.substituto_para,
            Ocupacao.id_ocupacao,
            Cargo.exclusivo
        )
        .select_from(Pessoa)
        .join(Ocupacao, Ocupacao.id_pessoa == Pessoa.id_pessoa, isouter=True)
        .join(Cargo, Cargo.id_cargo == Ocupacao.id_cargo, isouter=True)
        .join(Orgao, Orgao.id_orgao == Cargo.id_orgao, isouter=True)
    ),

    "orgao": lambda: (
        select(
            Pessoa.nome, Cargo.nome, Orgao.nome,
            Ocupacao.data_inicio, Ocupacao.data_fim,
            Ocupacao.mandato, 
            Ocupacao.observacoes,
            Cargo.substituto_para,
            Ocupacao.id_ocupacao,
            Cargo.exclusivo
        )
        .select_from(Orgao)
        .join(Cargo, Cargo.id_orgao == Orgao.id_orgao, isouter=True)
        .join(Ocupacao, Ocupacao.id_cargo == Cargo.id_cargo, isouter=True)
        .join(Pessoa, Pessoa.id_pessoa == Ocupacao.id_pessoa, isouter=True)
    ),

    "cargo": lambda: (
        select(
            Pessoa.nome, Cargo.nome, Orgao.nome,
            Ocupacao.data_inicio, Ocupacao.data_fim,
            Ocupacao.mandato,
            Ocupacao.observacoes,
            Cargo.substituto_para,
            Ocupacao.id_ocupacao,
            Cargo.exclusivo
        )
        .select_from(Cargo)
        .join(Orgao, Orgao.id_orgao == Cargo.id_orgao, isouter=True)
        .join(Ocupacao, Ocupacao.id_cargo == Cargo.id_cargo, isouter=True)
        .join(Pessoa, Pessoa.id_pessoa == Ocupacao.id_pessoa, isouter=True)
    ),

    "flat": lambda: (
        select(
            Pessoa.nome, Cargo.nome, Orgao.nome,
            Ocupacao.data_inicio, Ocupacao.data_fim,
            Ocupacao.mandato,
            Ocupacao.observacoes,
            Cargo.substituto_para,
            Ocupacao.id_ocupacao,
            Cargo.exclusivo
        )
        .join(Ocupacao, Ocupacao.id_pessoa == Pessoa.id_pessoa)
        .join(Cargo, Cargo.id_cargo == Ocupacao.id_cargo)
        .join(Orgao, Orgao.id_orgao == Cargo.id_orgao)
    )
}

# Mapeamento: "Campo Query" -> "Chave do Dicionário Python"
CHAVES_ORDENAVEIS = {
    "pessoa": "pessoa",
    "nome": "pessoa",
    "cargo": "cargo",
    "orgao": "orgao",
    "data_inicio": "data_inicio",
    "data_fim": "data_fim",
    "exclusivo": "exclusivo",
}


def safe_key(valor):
    if valor is None:
        return (0, None)
    return (1, valor)


def verificar_eligibilidade(id_pessoa: int, id_cargo: int, data_inicio, session: Session) -> bool:
    """Verifica se a pessoa é elegível para ocupar o cargo na data de início."""
    
    cargo = session.get(Cargo, id_cargo)

    # Regra 0: se o cargo não é exclusivo, qualquer pessoa é elegível
    if not cargo.exclusivo:
        return True
    

    # Regra 1: se alguém já ocupa o cargo na data de início, não é elegível
    pessoa = session.get(Pessoa, id_pessoa)

    
    # Regra 2: se a pessoa completar o terceiro mandato consecutivo, não é elegível




    

    return True


def obter_chave_ordenacao(sort_by_order_str: str) -> Tuple[Callable[[Dict[str, Any]], Any], bool]:
    """
    Retorna a chave de ordenação (função itemgetter ou uma função lambda customizada) e a direção.
    """
    try:
        chave_raw, order_raw = sort_by_order_str.split(",")
    except ValueError:
        return None, False

    chave_processada = chave_raw.strip().lower()
    order_processada = order_raw.strip().lower()
    
    chave_final = CHAVES_ORDENAVEIS.get(chave_processada)
    reverse = order_processada == "desc"

    if chave_final is None:
        return None, False
    
    return chave_final, reverse


def aplicar_filtros(query, busca, ativo, mandato, tipo):
    filtro = parse_filtro(busca, tipo) if busca else None
    where_clause = traduzir_parsing_result(filtro) if filtro else None

    if where_clause is not None:
        query = query.where(where_clause)

    if ativo == "ativos":
        query = query.where(Pessoa.ativo == True)
    elif ativo == "inativos":
        query = query.where(Pessoa.ativo == False)

    if mandato == "vigente":
        query = query.where(
            and_(or_(Ocupacao.data_inicio <= func.current_date(), Ocupacao.data_inicio == None),
                or_(Ocupacao.data_fim == None, Ocupacao.data_fim >= func.current_date())))
        
    elif mandato == "encerrado":
        query = query.where(Ocupacao.data_fim < func.current_date())

    elif mandato == "futuro":
        query = query.where(Ocupacao.data_inicio > func.current_date())
    
    return query




def montar_query(tipo, busca, ativo, mandato):
    if tipo not in QUERY_BASE:
        raise ValueError("Tipo inválido")

    query = QUERY_BASE[tipo]()
    query = aplicar_filtros(query, busca, ativo, mandato, tipo if tipo != "flat" else "pessoa")

    return query


# Busca agrupada por pessoa
def core_busca_generica(
    session: Session,
    tipo: str,
    busca: str = "",
    ativo: str = "todos",
    mandato: str = "todos",
    sort_by: str = "",
) -> List[Dict[str, Any]]:
    """
    Executa a busca, agrupa e ordena os resultados em memória,
    pronto para ser consumido por endpoints ou serviços internos.
    """
    try:
        # 1. MONTAGEM DA QUERY SQL
        # Esta função não deve mais chamar aplicar_ordenacao no SQLAlchemy.
        query = montar_query(tipo, busca, ativo, mandato)

        # 2. EXECUÇÃO DA QUERY
        results = session.exec(query).all()

        # 3. PRÉ-PROCESSAMENTO DA ORDENAÇÃO
        if sort_by:
            sort_key, reverse_order = obter_chave_ordenacao(sort_by)
        else:
            sort_key, reverse_order = None, False


        agrupado = defaultdict(list)
        resultados_agrupados = []

        # Desempacotamento padronizado para o loop (total de 10 colunas)
        # Campos: 0:nome_pessoa, 1:nome_cargo, 2:nome_orgao, 3:data_inicio, 4:data_fim, 
        #         5:mandato, 6:observacoes, 7:substituto_para, 8:id_ocupacao, 9:exclusivo

        if tipo == "pessoa":
            for r in results:
                nome = r[0]
                agrupado[nome].append({
                    "cargo": r[1], "orgao": r[2], "data_inicio": r[3], "data_fim": r[4], 
                    "mandato": r[5], "observacoes": r[6], "substituto_para": r[7], 
                    "id_ocupacao": r[8], "exclusivo": r[9]
                })
            resultados_agrupados = [{"pessoa": nome, "cargos": cargos or []} 
                                    for nome, cargos in agrupado.items()]

        elif tipo == "orgao":
            for r in results:
                orgao_nome = r[2]
                agrupado[orgao_nome].append({
                    "cargo": r[1], "pessoa": r[0], "data_inicio": r[3], "data_fim": r[4], 
                    "mandato": r[5], "observacoes": r[6], "substituto_para": r[7], 
                    "id_ocupacao": r[8], "exclusivo": r[9]
                })
            resultados_agrupados = [{"orgao": nome, "cargos": cargos or []} 
                                    for nome, cargos in agrupado.items()]

        elif tipo == "cargo":
            for r in results:
                chave = (r[1], r[2]) # (cargo, orgao)
                agrupado[chave].append({
                    "orgao": r[2], "pessoa": r[0], "data_inicio": r[3], "data_fim": r[4], 
                    "mandato": r[5], "observacoes": r[6], "substituto_para": r[7], 
                    "id_ocupacao": r[8], "exclusivo": r[9]
                })
            resultados_agrupados = [{"cargo": cargo, "orgao": orgao, "ocupacoes": cargos or []} 
                                    for (cargo, orgao), cargos in agrupado.items()]

        elif tipo == "flat":
            resultados_agrupados = [{
                "pessoa": r[0], "cargo": r[1], "orgao": r[2], "data_inicio": r[3], "data_fim": r[4], 
                "mandato": r[5], "observacoes": r[6], "substituto_para": r[7], 
                "id_ocupacao": r[8], "exclusivo": r[9]
            } for r in results]

        # 4. ORDENAÇÃO EM MEMÓRIA

        if sort_key is None:
            return resultados_agrupados
        
        
        if sort_key == tipo:
            resultados_agrupados = sorted(resultados_agrupados, key= lambda x: safe_key(x[sort_key]), reverse=reverse_order)
            return resultados_agrupados
        
        if tipo == "flat":
            resultados_agrupados = sorted(resultados_agrupados, key= lambda x: safe_key(x[sort_key]), reverse=reverse_order)
            return resultados_agrupados
        
        # Vamos ordenar em cada grupo
        for linha in resultados_agrupados:
            if "cargos" in linha:
                linha["cargos"] = sorted(linha["cargos"], key= lambda x: safe_key(x[sort_key]), reverse=reverse_order)
            elif "ocupacoes" in linha:
                linha["ocupacoes"] = sorted(linha["ocupacoes"], key= lambda x: safe_key(x[sort_key]), reverse=reverse_order)
        
        return resultados_agrupados
        
        
    except Exception as e:
        # Captura erros de montagem de query, execução ou processamento.
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================================
# ENDPOINT BUSCA GENÉRICA (SIMPLIFICADO)
# =========================================================================

@router.get("/busca/")
def busca_generica(
    busca: str = Query("", description="Prefixo para busca"),
    ativo: str = Query("todos", description="Filtra por ativo/inativo"),
    mandato: str = Query("todos", description="Filtra por vigência de mandato ('vigente', 'encerrado', 'futuro', 'todos')"),
    session: Session = Depends(get_session),
    tipo: str = Query("pessoa", description="Tipo de busca"),
    sort_by: str = Query(None, description="Campo para ordenar (ex: 'nome,asc')"),
):
    # Chama a função core, transferindo a lógica para ela.
    return core_busca_generica(
        session=session,
        tipo=tipo,
        busca=busca,
        ativo=ativo,
        mandato=mandato,
        sort_by=sort_by
    )
