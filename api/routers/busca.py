from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlmodel import Session, func, select
from models import Orgao, Cargo, Pessoa, Portaria, Ocupacao
from database import get_session
from collections import defaultdict
from search_grammar.parsers import parse_filtro, traduzir_parsing_result

router = APIRouter(
    prefix="/api",
    tags=["Busca"]
)


# Busca agrupada por pessoa
@router.get("/busca/agrupada/pessoa")
def busca_agrupada_por_pessoa(
    busca: str = Query("", description="Prefixo para busca"),
    ativo: str = Query("todos", description="Filtra por ativo/inativo (todos|ativos|inativos)"),
    mandato: str = Query("todos", description="Filtra por mandato (todos|vigente|encerrado)"),
    session: Session = Depends(get_session)):

    try:
        filtro = parse_filtro(busca, "Pessoa") if busca else None

        where_clause = traduzir_parsing_result(filtro) if filtro else None
        
        query = (select(Pessoa.nome, Cargo.nome, Orgao.nome, Ocupacao.data_inicio, Ocupacao.data_fim, Ocupacao.mandato)
                 .join(Ocupacao, Ocupacao.id_pessoa == Pessoa.id_pessoa)
                 .join(Cargo, Cargo.id_cargo == Ocupacao.id_cargo)
                 .join(Orgao, Orgao.id_orgao == Cargo.id_orgao))
        
        if where_clause is not None:
            query = query.where(where_clause)
        
        if busca:
            print(busca)

        if ativo == "inativos":
            query = query.where(Pessoa.ativo == False)
        elif ativo == "ativos":
            query = query.where(Pessoa.ativo == True)
        
        if mandato == "vigente":
            query = query.where(Ocupacao.data_fim == None)
        elif mandato == "encerrado":
            query = query.where(Ocupacao.data_fim <= func.current_date())


        results = session.exec(query).all()

        agrupado = defaultdict(list)

        for nome, id_cargo, id_orgao, data_inicio, data_fim, mandato in results:
            agrupado[nome].append({"cargo": id_cargo, "orgao": id_orgao, "data_inicio": data_inicio, "data_fim": data_fim, "mandato": mandato})

        return [{"nome": nome, "cargos": cargos or []} for nome, cargos in agrupado.items()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Busca agrupada por órgão
@router.get("/busca/agrupada/orgao")
def busca_agrupada_por_orgao(
    busca: str = Query("", description="Prefixo para busca"),
    ativo: str = Query("todos", description="Filtra por ativo/inativo (todos|ativos|inativos)"),
    mandato: str = Query("todos", description="Filtra por mandato (todos|vigente|encerrado)"),
    session: Session = Depends(get_session)):

    try:
        filtro = parse_filtro(busca, "Orgao") if busca else None
        where_clause = traduzir_parsing_result(filtro) if filtro else None
    
        query = (select(Orgao.nome, Cargo.nome, Pessoa.nome, Ocupacao.data_inicio, Ocupacao.data_fim, Ocupacao.mandato)
                 .join(Ocupacao, Ocupacao.id_cargo == Cargo.id_cargo)
                 .join(Pessoa, Ocupacao.id_pessoa == Pessoa.id_pessoa)
                 .join(Orgao, Orgao.id_orgao == Cargo.id_orgao))
        
        if where_clause is not None:
            query = query.where(where_clause)

        if busca:
            query = query.where(Orgao.nome.ilike(f"{busca}%"))

        if ativo == "inativos":
            query = query.where(Orgao.ativo == False)
        elif ativo == "ativos":
            query = query.where(Orgao.ativo == True)

        if mandato == "vigente":
            query = query.where(Ocupacao.data_fim == None)
        elif mandato == "encerrado":
            query = query.where(Ocupacao.data_fim <= func.current_date())


        results = session.exec(query).all()

        agrupado = defaultdict(list)

        for nome, id_cargo, id_pessoa, data_inicio, data_fim, mandato in results:
            agrupado[nome].append({"cargo": id_cargo, "pessoa": id_pessoa, "data_inicio": data_inicio, "data_fim": data_fim, "mandato": mandato})

        return [{"orgao": nome, "cargos": cargos or []} for nome, cargos in agrupado.items()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Busca agrupada por cargo
@router.get("/busca/agrupada/cargo")
def busca_agrupada_por_cargo(
    busca: str = Query("", description="Prefixo para busca"),
    ativo: str = Query("todos", description="Filtra por ativo/inativo (todos|ativos|inativos)"),
    mandato: str = Query("todos", description="Filtra por mandato (todos|vigente|encerrado)"),
    session: Session = Depends(get_session)):
    try:

        filtro = parse_filtro(busca, "Cargo") if busca else None
        where_clause = traduzir_parsing_result(filtro) if filtro else None

        query = (select(Cargo.nome, Orgao.nome, Pessoa.nome, Ocupacao.data_inicio, Ocupacao.data_fim, Ocupacao.mandato)
                 .join(Ocupacao, Ocupacao.id_cargo == Cargo.id_cargo)
                 .join(Pessoa, Ocupacao.id_pessoa == Pessoa.id_pessoa)
                 .join(Orgao, Orgao.id_orgao == Cargo.id_orgao))
        
        if where_clause is not None:
            query = query.where(where_clause)

        if busca:
            query = query.where(Cargo.nome.ilike(f"{busca}%"))

        if ativo == "inativos":
            query = query.where(Cargo.ativo == False)
        elif ativo == "ativos":
            query = query.where(Cargo.ativo == True)

        if mandato == "vigente":
            query = query.where(Ocupacao.data_fim == None)
        elif mandato == "encerrado":
            query = query.where(Ocupacao.data_fim <= func.current_date())


        results = session.exec(query).all()

        agrupado = defaultdict(list)

        for cargo_nome, orgao_nome, pessoa_nome, data_inicio, data_fim, mandato in results:
            chave = (cargo_nome, orgao_nome)
            agrupado[chave].append({
                "pessoa": pessoa_nome,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "mandato": mandato
            })

        return [{"cargo": cargo_nome, "orgao": orgao_nome, "ocupacoes": ocupacoes or []} for (cargo_nome, orgao_nome), ocupacoes in agrupado.items()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



