from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlmodel import Session, func, select
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
            Ocupacao.id_ocupacao
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
            Ocupacao.id_ocupacao
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
            Ocupacao.id_ocupacao
        )
        .select_from(Cargo)
        .join(Orgao, Orgao.id_orgao == Cargo.id_orgao, isouter=True)
        .join(Ocupacao, Ocupacao.id_cargo == Cargo.id_cargo, isouter=True)
        .join(Pessoa, Pessoa.id_pessoa == Ocupacao.id_pessoa, isouter=True)
    ),

    "flat": lambda: (
        select(
            Pessoa.nome, Cargo.id_cargo, Orgao.id_orgao,
            Ocupacao.data_inicio, Ocupacao.data_fim,
            Ocupacao.mandato,
            Ocupacao.observacoes,
            Cargo.substituto_para,
            Ocupacao.id_ocupacao
        )
        .join(Ocupacao, Ocupacao.id_pessoa == Pessoa.id_pessoa)
        .join(Cargo, Cargo.id_cargo == Ocupacao.id_cargo)
        .join(Orgao, Orgao.id_orgao == Cargo.id_orgao)
    )
}

ORDENAVEIS = {
    "nome": Pessoa.nome,
    "cargo": Cargo.nome,
    "orgao": Orgao.nome,
    "data_inicio": Ocupacao.data_inicio,
    "data_fim": Ocupacao.data_fim,
}


def aplicar_filtros(query, busca, ativo, mandato):
    filtro = parse_filtro(busca, "Pessoa") if busca else None
    where_clause = traduzir_parsing_result(filtro) if filtro else None

    if where_clause:
        query = query.where(where_clause)

    if ativo == "ativos":
        query = query.where(Pessoa.ativo == True)
    elif ativo == "inativos":
        query = query.where(Pessoa.ativo == False)

    if mandato == "vigente":
        query = query.where(Ocupacao.data_fim == None)
    elif mandato == "encerrado":
        query = query.where(Ocupacao.data_fim <= func.current_date())

    return query


def aplicar_ordenacao(query, campo, ordem):
    if campo in ORDENAVEIS:
        coluna = ORDENAVEIS[campo]
        query = query.order_by(coluna.asc() if ordem == "asc" else coluna.desc())
    return query



def montar_query(tipo, busca, ativo, mandato, sort_by=None, order=None):
    if tipo not in QUERY_BASE:
        raise ValueError("Tipo inválido")

    query = QUERY_BASE[tipo]()

    query = aplicar_filtros(query, busca, ativo, mandato)

    if sort_by:
        query = aplicar_ordenacao(query, sort_by, order)

    return query



# Busca agrupada por pessoa
@router.get("/busca/")
def busca_generica(
    busca: str = Query("", description="Prefixo para busca"),
    ativo: str = Query("todos", description="Filtra por ativo/inativo (todos|ativos|inativos)"),
    mandato: str = Query("todos", description="Filtra por mandato (todos|vigente|encerrado)"),
    session: Session = Depends(get_session),
    search_type: str = Query("pessoa", description="Tipo de busca (pessoa|orgao|cargo|flat)"),
    sort_by: str = Query(None, description="Campo para ordenar"),
    order: str = Query("asc", description="Ordem de ordenação (asc|desc)")):

    try:
        query = montar_query(search_type, busca, ativo, mandato, sort_by=sort_by, order=order)

        results = session.exec(query).all()

        agrupado = defaultdict(list)

        if search_type == "pessoa":
            for nome, cargo, orgao, data_inicio, data_fim, mandato, observacoes, substituto_para, id_ocupacao in results:
                agrupado[nome].append({"cargo": cargo, "orgao": orgao, "data_inicio": data_inicio, "data_fim": data_fim, "mandato": mandato, "id_ocupacao": id_ocupacao, "observacoes": observacoes, "substituto_para": substituto_para})
            return [{"pessoa": nome, "cargos": cargos or []} for nome, cargos in agrupado.items()]
            
        if search_type == "orgao":
            for nome, cargo, orgao, data_inicio, data_fim, mandato, observacoes, substituto_para, id_ocupacao in results:
                agrupado[orgao].append({"cargo": cargo, "pessoa": nome, "data_inicio": data_inicio, "data_fim": data_fim, "mandato": mandato, "id_ocupacao": id_ocupacao, "observacoes": observacoes, "substituto_para": substituto_para})
            return [{"orgao": nome, "cargos": cargos or []} for nome, cargos in agrupado.items()]
        
        if search_type == "cargo":
            for nome, cargo, orgao, data_inicio, data_fim, mandato, observacoes, substituto_para, id_ocupacao in results:
                chave = (cargo, orgao)
                agrupado[chave].append({"orgao": orgao, "pessoa": nome, "data_inicio": data_inicio, "data_fim": data_fim, "mandato": mandato, "id_ocupacao": id_ocupacao, "observacoes": observacoes, "substituto_para": substituto_para})
            return [{"cargo": cargo, "orgao": orgao, "ocupacoes": cargos or []} for (cargo, orgao), cargos in agrupado.items()]
        
        if search_type == "flat":
            return [{
                "pessoa": nome,
                "cargo": id_cargo,
                "orgao": id_orgao,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "mandato": mandato,
                "id_ocupacao": id_ocupacao,
                "observacoes": observacoes,
                "substituto_para": substituto_para,
            } for nome, id_cargo, id_orgao, data_inicio, data_fim, mandato, observacoes, substituto_para, id_ocupacao in results]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
