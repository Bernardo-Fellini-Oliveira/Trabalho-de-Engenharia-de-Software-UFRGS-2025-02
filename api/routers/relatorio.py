import csv
from typing import Any, Literal
from fastapi import APIRouter, Depends
from fastapi.params import Query
from fastapi.responses import StreamingResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO, StringIO
from pydantic import BaseModel
from sqlmodel import Session, select, func

from routers.busca import montar_query
from database import get_session
from models.cargo import Cargo
from models.ocupacao import Ocupacao
from models.orgao import Orgao
from models.pessoa import Pessoa
from search_grammar.parsers import parse_filtro, traduzir_parsing_result

router = APIRouter(
    prefix="/api/relatorio",
    tags=["Relatório"]
)



from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer

def gerar_pdf_agrupado(dados, elementos, styles, group_by: str = "cargo"):
    """
    Gera um PDF (adiciona uma tabela a `elementos`) com os dados agrupados conforme `group_by`.
    group_by: "cargo" | "pessoa" | "orgao" | "flat"
    - espera `dados` no formato:
      * cargo: [{"cargo": "...", "orgao": "...", "ocupacoes": [{...}, ...]}, ...]
      * pessoa: [{"nome": "...", "cargos": [{...}, ...]}, ...]  (cada item em `cargos` tem keys: cargo, orgao, data_inicio, data_fim, mandato)
      * orgao: [{"orgao": "...", "cargos": [{...}, ...]}, ...]
      * flat: lista de linhas planas no formato [{"pessoa":..,"cargo":..,"orgao":..,"data_inicio":..,"data_fim":..,"mandato":..}, ...]
    """

    # configuração de colunas por modo (rótulos e ordem)
    if group_by == "cargo":
        header = ["Cargo", "Órgão", "Pessoa", "Início", "Fim", "Mandato", "Observações"]
    elif group_by == "pessoa":
        header = ["Pessoa", "Cargo", "Órgão", "Início", "Fim", "Mandato", "Observações"]
    elif group_by == "orgao":
        header = ["Órgão", "Cargo", "Pessoa", "Início", "Fim", "Mandato", "Observações"]
    elif group_by == "flat":
        header = ["Pessoa", "Cargo", "Órgão", "Início", "Fim", "Mandato", "Observações"]
    else:
        raise ValueError("group_by inválido — use 'cargo','pessoa','orgao' ou 'flat'.")

    table_data = [header]
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
    ]
    
    next_row_idx = 1  # primeira linha após header
    spans_to_add = []  # acumula spans (start_row, end_row, col_start, col_end)

    # monta linhas dependendo do modo
    if group_by == "flat":
        # dados já são linhas planas
        for item in dados:
            pessoa = item.get("pessoa", "-")
            cargo = item.get("cargo", "-")
            orgao = item.get("orgao", "-")
            inicio = item.get("data_inicio", "-") or "-"
            fim = item.get("data_fim", "-") or "-"
            mandato = str(item.get("mandato", "-"))
            observacoes = item.get("observacoes", "-")
            table_data.append([pessoa, cargo, orgao, inicio, fim, mandato, observacoes])
            next_row_idx += 1

    else:
        # modos agrupados: percorre blocos
        for bloco in dados:
            # extrai a lista de ocupações dependendo do formato
            if group_by == "cargo":
                ocupacoes = bloco.get("ocupacoes", [])
                label1 = bloco.get("cargo", "-")
                label2 = bloco.get("orgao", "-")
                # cada ocupação: pessoa, inicio, fim, mandato, id_ocupacao
                rows = [
                    [o.get("pessoa", "-"), o.get("data_inicio", "-") or "-", o.get("data_fim", "-") or "-", str(o.get("mandato", "-")), o.get("observacoes", "-")]
                    for o in ocupacoes
                ]
                # para este layout precisamos inserir Cargo, Orgão nas duas primeiras colunas
                if not ocupacoes:
                    table_data.append([label1, label2, "Sem ocupações.", "-", "-", "-", "-"])
                    style_cmds.append(("SPAN", (2, next_row_idx), (5, next_row_idx)))
                    style_cmds.append(("VALIGN", (0, next_row_idx), (1, next_row_idx), "MIDDLE"))
                    style_cmds.append(("ALIGN", (2, next_row_idx), (5, next_row_idx), "LEFT"))
                    next_row_idx += 1
                    continue

                start = next_row_idx
                for i, r in enumerate(rows):
                    pessoa, inicio, fim, mandato, observacoes = r
                    if i == 0:
                        table_data.append([label1, label2, pessoa, inicio, fim, mandato, observacoes])
                    else:
                        table_data.append(["", "", pessoa, inicio, fim, mandato, observacoes])
                    next_row_idx += 1
                end = next_row_idx - 1
                if start <= end and (end - start + 1) >= 1:
                    # mesclar col 0 e 1 entre start..end
                    spans_to_add.append((start, end, 0, 0))  # cargo col
                    spans_to_add.append((start, end, 1, 1))  # orgao col

            elif group_by == "pessoa":
                ocupacoes = bloco.get("cargos", [])
                label = bloco.get("pessoa", "-")
                if not ocupacoes:
                    table_data.append([label, "—", "—", "-", "-", "-", "-"])
                    style_cmds.append(("SPAN", (1, next_row_idx), (6, next_row_idx)))
                    style_cmds.append(("VALIGN", (0, next_row_idx), (0, next_row_idx), "MIDDLE"))
                    style_cmds.append(("ALIGN", (1, next_row_idx), (6, next_row_idx), "LEFT"))
                    next_row_idx += 1
                    continue

                start = next_row_idx
                for i, o in enumerate(ocupacoes):
                    cargo = o.get("cargo", "-")
                    orgao = o.get("orgao", "-")
                    inicio = o.get("data_inicio", "-") or "-"
                    fim = o.get("data_fim", "-") or "-"
                    mandato = "" if o.get("mandato") is None else str(o.get("mandato"))
                    observacoes = o.get("observacoes", "-")
                    if i == 0:
                        table_data.append([label, cargo, orgao, inicio, fim, mandato, observacoes])
                    else:
                        table_data.append(["", cargo, orgao, inicio, fim, mandato, observacoes])
                    next_row_idx += 1
                end = next_row_idx - 1
                spans_to_add.append((start, end, 0, 0))  # mesclar coluna Pessoa

            elif group_by == "orgao":
                ocupacoes = bloco.get("cargos", [])
                label = bloco.get("orgao", "-")
                if not ocupacoes:
                    table_data.append([label, "—", "—", "-", "-", "-", "-"])
                    style_cmds.append(("SPAN", (1, next_row_idx), (6, next_row_idx)))
                    style_cmds.append(("VALIGN", (0, next_row_idx), (0, next_row_idx), "MIDDLE"))
                    style_cmds.append(("ALIGN", (1, next_row_idx), (6, next_row_idx), "LEFT"))
                    next_row_idx += 1
                    continue

                start = next_row_idx
                for i, o in enumerate(ocupacoes):
                    cargo = o.get("cargo", "-")
                    pessoa = o.get("pessoa", "-")
                    inicio = o.get("data_inicio", "-") or "-"
                    fim = o.get("data_fim", "-") or "-"
                    mandato = "" if o.get("mandato") is None else str(o.get("mandato"))
                    observacoes = o.get("observacoes", "-")
                    if i == 0:
                        table_data.append([label, cargo, pessoa, inicio, fim, mandato, observacoes])
                    else:
                        table_data.append(["", cargo, pessoa, inicio, fim, mandato, observacoes])
                    next_row_idx += 1
                end = next_row_idx - 1
                spans_to_add.append((start, end, 0, 0))  # mesclar coluna Órgão

    # aplica spans acumulados no estilo
    for start, end, c0, c1 in spans_to_add:
        style_cmds.append(("SPAN", (c0, start), (c1, end)))
        # centraliza verticalmente a célula mesclada
        style_cmds.append(("VALIGN", (c0, start), (c1, end), "MIDDLE"))
        style_cmds.append(("ALIGN", (c0, start), (c1, end), "CENTER"))

    tabela = Table(table_data, repeatRows=1)
    tabela.setStyle(TableStyle(style_cmds))

    elementos.append(tabela)
    elementos.append(Spacer(1, 18))




# TO DO: recuperar busca com filtros para então gerar o relatório
# Evita de passar todos os dados entre frontend e backend
class ExportRequest(BaseModel):
    tipo: Literal["cargo", "pessoa", "orgao", "flat"]
    busca: str = ""
    ativo: Literal["todos", "ativos", "inativos"] = "todos"
    mandato: Literal["todos", "vigente", "encerrado"] = "todos"
    sort_by: str = "nome"     # ou cargo, orgao, data_inicio, data_fim
    order: Literal["asc", "desc"] = "asc"



def montar_query_export(req: ExportRequest, session: Session):

    base = montar_query(
        tipo=req.tipo,
        busca=req.busca,
        ativo=req.ativo,
        mandato=req.mandato,
        sort_by=req.sort_by,
        order=req.order
    )


    resultados = session.exec(base).all()

    print("Resultados:", resultados)
    # ----------------------------
    # AGRUPAMENTO
    # ----------------------------
    if req.tipo == "flat":
        return resultados

    agrupado = {}

    if req.tipo == "pessoa":
        chave = lambda r: r[0] # pessoa
    elif req.tipo == "cargo":
        chave = lambda r: (r[1], r[2])  # (cargo, orgao)
    elif req.tipo == "orgao":
        chave = lambda r: r[2] # orgao

    for r in resultados:
        print("Processando:", r)
        k = chave(r)
        agrupado.setdefault(k, []).append(r)

    # Transformar no formato esperado pelo gerador PDF
    if req.tipo == "pessoa":
        return [
            {
                "pessoa": pessoa,
                "cargos": [
                    {
                        "cargo": r[1],
                        "orgao": r[2],
                        "data_inicio": r[3],
                        "data_fim": r[4],
                        "mandato": r[5],
                        "observacoes": r[6],
                    }
                    for r in lista
                ],
            }
            for pessoa, lista in agrupado.items()
        ]

    if req.tipo == "orgao":
        return [
            {
                "orgao": orgao,
                "cargos": [
                    {
                        "pessoa": r[0],
                        "cargo": r[1],
                        "data_inicio": r[3],
                        "data_fim": r[4],
                        "mandato": r[5],
                        "observacoes": r[6],
                    }
                    for r in lista
                ],
            }
            for orgao, lista in agrupado.items()
        ]

    if req.tipo == "cargo":
        return [
            {
                "cargo": cargo,
                "orgao": orgao,
                "ocupacoes": [
                    {
                        "pessoa": r[0],
                        "data_inicio": r[3],
                        "data_fim": r[4],
                        "mandato": r[5],
                        "observacoes": r[6],
                    }
                    for r in lista
                ],
            }
            for (cargo, orgao), lista in agrupado.items()
        ]
    
@router.post("/export/pdf")
def export_pdf(req: ExportRequest, session: Session = Depends(get_session)):
    dados = montar_query_export(req, session)

    print(dados)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elementos = []

    elementos.append(Spacer(1, 12))

    if req.tipo in ("cargo", "pessoa", "orgao"):
        gerar_pdf_agrupado(dados, elementos, styles, group_by=req.tipo)
    else:
        gerar_pdf_agrupado(dados, elementos, styles, group_by="flat")

    doc.build(elementos)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=relatorio.pdf"}
    )




@router.post("/export/csv")
def export_csv(req: ExportRequest, session: Session = Depends(get_session)):

    # ========= 1) Refaz a consulta ao banco ==========
    filtro = parse_filtro(req.busca, "Pessoa") if req.busca else None
    where_clause = traduzir_parsing_result(filtro) if filtro else None

    query = (
        select(
            Pessoa.nome,
            Cargo.nome,
            Orgao.nome,
            Ocupacao.data_inicio,
            Ocupacao.data_fim,
            Ocupacao.mandato,
            Ocupacao.observacoes
        )
        .join(Ocupacao, Ocupacao.id_pessoa == Pessoa.id_pessoa)
        .join(Cargo, Cargo.id_cargo == Ocupacao.id_cargo)
        .join(Orgao, Orgao.id_orgao == Cargo.id_orgao)
    )

    if where_clause is not None:
        query = query.where(where_clause)

    if req.ativo == "inativos":
        query = query.where(Pessoa.ativo == False)
    elif req.ativo == "ativos":
        query = query.where(Pessoa.ativo == True)

    if req.mandato == "vigente":
        query = query.where(Ocupacao.data_fim == None)
    elif req.mandato == "encerrado":
        query = query.where(Ocupacao.data_fim <= func.current_date())

    rows = session.exec(query).all()

    print("Rows: ", rows)
    # ========= 2) Agrupa conforme req.tipo ==========

    if req.tipo == "flat":
        agrupado = rows  # já está flat
    else:
        agrupado = {}
        for nome_pessoa, nome_cargo, nome_orgao, ini, fim, mandato, observacoes in rows:
            if req.tipo == "cargo":
                chave = (nome_cargo, nome_orgao)
            elif req.tipo == "pessoa":
                chave = nome_pessoa
            elif req.tipo == "orgao":
                chave = nome_orgao

            agrupado.setdefault(chave, []).append({
                "pessoa": nome_pessoa,
                "cargo": nome_cargo,
                "orgao": nome_orgao,
                "data_inicio": ini,
                "data_fim": fim,
                "mandato": mandato,
                "observacoes": observacoes
            })

    # ========= 3) Monta o CSV ==========
    buffer = StringIO()
    writer = csv.writer(buffer)

    # Cabeçalho universal
    writer.writerow(["Pessoa", "Cargo", "Órgão", "Início", "Fim", "Mandato", "Observações"])

    if req.tipo == "flat":
        for r in rows:
            pessoa, cargo, orgao, ini, fim, mandato, observacoes = r
            writer.writerow([
                pessoa, cargo, orgao,
                ini or "", fim or "", mandato, observacoes or ""
            ])
    else:
        for chave, ocupacoes in agrupado.items():
            # Escreve um bloco de título
            if req.tipo == "cargo":
                cargo, orgao = chave
                for oc in ocupacoes:
                    writer.writerow([oc["pessoa"], cargo, orgao, oc["data_inicio"] or "", oc["data_fim"] or "", oc["mandato"], oc["observacoes"] or ""])

            elif req.tipo == "pessoa":
                for oc in ocupacoes:
                    writer.writerow([chave, oc["cargo"], oc["orgao"], oc["data_inicio"] or "", oc["data_fim"] or "", oc["mandato"], oc["observacoes"] or ""])
            elif req.tipo == "orgao":
                for oc in ocupacoes:
                    writer.writerow([oc["pessoa"], oc["cargo"], chave, oc["data_inicio"] or "", oc["data_fim"] or "", oc["mandato"], oc["observacoes"] or ""])

    # ========= 4) Retorno como arquivo ==========
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=relatorio.csv"}
    )

