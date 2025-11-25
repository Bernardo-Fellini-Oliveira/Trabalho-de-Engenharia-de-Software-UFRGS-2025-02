import csv
from typing import Any, List, Literal
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO, StringIO
from pydantic import BaseModel
from sqlmodel import Session

from reportlab.platypus import Paragraph

from routers.busca import core_busca_generica
from database import get_session


router = APIRouter(
    prefix="/api/relatorio",
    tags=["Relatório"]
)



from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer


def secure_get_dados(field: str, dados: List[Any], standard_value: Any = None):
    value = dados.get(field, standard_value)
    value = value if value is not None else standard_value
    return value
 
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

    BLANK_SYMBOL = "-"

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

            pessoa = Paragraph(item.get("pessoa") or BLANK_SYMBOL, styles)
            cargo = Paragraph(item.get("cargo") or BLANK_SYMBOL, styles)
            orgao = Paragraph(item.get("orgao") or BLANK_SYMBOL, styles)
            inicio = item.get("data_inicio") or BLANK_SYMBOL
            fim = item.get("data_fim") or BLANK_SYMBOL
            exclusivo = item.get("exclusivo", False)
            mandato = str(item.get("mandato")) if exclusivo and item.get("mandato") is not None else BLANK_SYMBOL
            observacoes = Paragraph(item.get("observacoes") or BLANK_SYMBOL, styles)
            
            table_data.append([pessoa, cargo, orgao, inicio, fim, mandato, observacoes])
            next_row_idx += 1

    else:
        # modos agrupados: percorre blocos
        for bloco in dados:
    
            # extrai a lista de ocupações dependendo do formato
            if group_by == "cargo":
                ocupacoes = bloco.get("ocupacoes", [])
                label1 = bloco.get("cargo", "")
                label2 = bloco.get("orgao", "")
                # cada ocupação: pessoa, inicio, fim, mandato, id_ocupacao

                
                rows = [
                    [secure_get_dados("pessoa", o, BLANK_SYMBOL),
                     o.get("data_inicio", BLANK_SYMBOL) or BLANK_SYMBOL, 
                     o.get("data_fim", BLANK_SYMBOL) or BLANK_SYMBOL, 
                     str(o.get("mandato", BLANK_SYMBOL)) if o.get("mandato") is not None else BLANK_SYMBOL, 
                     secure_get_dados("observacoes", o, BLANK_SYMBOL), 
                     o.get("exclusivo", False)]
                    for o in ocupacoes
                ]
                # para este layout precisamos inserir Cargo, Orgão nas duas primeiras colunas
                if not ocupacoes:
                    table_data.append([label1, label2, "Sem ocupações.", BLANK_SYMBOL, BLANK_SYMBOL, BLANK_SYMBOL, BLANK_SYMBOL])
                    style_cmds.append(("SPAN", (2, next_row_idx), (5, next_row_idx)))
                    style_cmds.append(("VALIGN", (0, next_row_idx), (1, next_row_idx), "MIDDLE"))
                    style_cmds.append(("ALIGN", (2, next_row_idx), (5, next_row_idx), "LEFT"))
                    next_row_idx += 1
                    continue

                start = next_row_idx
                for i, r in enumerate(rows):
                    pessoa, inicio, fim, mandato, observacoes, exclusivo = r
                    mandato = mandato if exclusivo and mandato else BLANK_SYMBOL
                    if i == 0:
                        table_data.append([label1, label2, pessoa, inicio, fim, mandato, observacoes])
                    else:
                        table_data.append([BLANK_SYMBOL, BLANK_SYMBOL, pessoa, inicio, fim, mandato, observacoes])
                    next_row_idx += 1
                end = next_row_idx - 1
                if start <= end and (end - start + 1) >= 1:
                    # mesclar col 0 e 1 entre start..end
                    spans_to_add.append((start, end, 0, 0))  # cargo col
                    spans_to_add.append((start, end, 1, 1))  # orgao col

            elif group_by == "pessoa":
                ocupacoes = bloco.get("cargos", [])
                label = bloco.get("pessoa", BLANK_SYMBOL)
                if not ocupacoes:
                    table_data.append([label, BLANK_SYMBOL, BLANK_SYMBOL, BLANK_SYMBOL, BLANK_SYMBOL, BLANK_SYMBOL, BLANK_SYMBOL])
                    style_cmds.append(("SPAN", (1, next_row_idx), (6, next_row_idx)))
                    style_cmds.append(("VALIGN", (0, next_row_idx), (0, next_row_idx), "MIDDLE"))
                    style_cmds.append(("ALIGN", (1, next_row_idx), (6, next_row_idx), "LEFT"))
                    next_row_idx += 1
                    continue

                start = next_row_idx
                for i, o in enumerate(ocupacoes):
                    
                    cargo = secure_get_dados("cargo", o, BLANK_SYMBOL)
                    orgao = secure_get_dados("orgao", o, BLANK_SYMBOL)
                    
                    inicio = o.get("data_inicio", BLANK_SYMBOL) or BLANK_SYMBOL
                    fim = o.get("data_fim", BLANK_SYMBOL) or BLANK_SYMBOL
                    mandato = BLANK_SYMBOL if o.get("mandato") is None else str(o.get("mandato"))
                    exclusivo = o.get("exclusivo", False)
                    if not exclusivo:
                        mandato = BLANK_SYMBOL

                    observacoes = Paragraph(secure_get_dados("observacoes", o, BLANK_SYMBOL), styles)

                    if i == 0:
                        table_data.append([label, cargo, orgao, inicio, fim, mandato, observacoes])
                    else:
                        table_data.append([BLANK_SYMBOL, cargo, orgao, inicio, fim, mandato, observacoes])
                    next_row_idx += 1
                end = next_row_idx - 1
                spans_to_add.append((start, end, 0, 0))  # mesclar coluna Pessoa

            elif group_by == "orgao":
                ocupacoes = bloco.get("cargos", [])
                label = bloco.get("orgao", BLANK_SYMBOL)
                if not ocupacoes:
                    table_data.append([label, BLANK_SYMBOL, BLANK_SYMBOL, BLANK_SYMBOL, BLANK_SYMBOL, BLANK_SYMBOL, BLANK_SYMBOL])
                    style_cmds.append(("SPAN", (1, next_row_idx), (6, next_row_idx)))
                    style_cmds.append(("VALIGN", (0, next_row_idx), (0, next_row_idx), "MIDDLE"))
                    style_cmds.append(("ALIGN", (1, next_row_idx), (6, next_row_idx), "LEFT"))
                    next_row_idx += 1
                    continue

                start = next_row_idx
                for i, o in enumerate(ocupacoes):
                    cargo = secure_get_dados("cargo", o, BLANK_SYMBOL)
                    pessoa = secure_get_dados("pessoa", o, BLANK_SYMBOL)
                    inicio = o.get("data_inicio", BLANK_SYMBOL) or BLANK_SYMBOL
                    fim = o.get("data_fim", BLANK_SYMBOL) or BLANK_SYMBOL
                    mandato = BLANK_SYMBOL if o.get("mandato") is None else str(o.get("mandato"))
                    exclusivo = o.get("exclusivo", False)
                    if not exclusivo:
                        mandato = BLANK_SYMBOL

                    observacoes = Paragraph(secure_get_dados("observacoes", o, BLANK_SYMBOL), styles)

                    if i == 0:
                        table_data.append([label, cargo, pessoa, inicio, fim, mandato, observacoes])
                    else:
                        table_data.append([BLANK_SYMBOL, cargo, pessoa, inicio, fim, mandato, observacoes])
                    next_row_idx += 1
                end = next_row_idx - 1
                spans_to_add.append((start, end, 0, 0))  # mesclar coluna Órgão

    # aplica spans acumulados no estilo
    for start, end, c0, c1 in spans_to_add:
        style_cmds.append(("SPAN", (c0, start), (c1, end)))
        # centraliza verticalmente a célula mesclada
        style_cmds.append(("VALIGN", (c0, start), (c1, end), "MIDDLE"))
        style_cmds.append(("ALIGN", (c0, start), (c1, end), "CENTER"))

    tabela = Table(table_data, repeatRows=1, colWidths=[80, 80, 100, 60, 60, 50, 150])
    tabela.setStyle(TableStyle(style_cmds))

    elementos.append(tabela)
    elementos.append(Spacer(1, 18))



class ExportRequest(BaseModel):
    tipo: Literal["cargo", "pessoa", "orgao", "flat"]
    busca: str = ""
    ativo: Literal["todos", "ativos", "inativos"] = "todos"
    mandato: Literal["todos", "vigente", "encerrado"] = "todos"
    sort_by: str = "" # ex: "pessoa,asc", "cargo,desc"



    
@router.post("/export/pdf")
def export_pdf(req: ExportRequest, session: Session = Depends(get_session)):
    dados = core_busca_generica(
        tipo=req.tipo,
        busca=req.busca,
        ativo=req.ativo,
        mandato=req.mandato,
        sort_by=req.sort_by,
        session=session
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elementos = []

    elementos.append(Spacer(1, 3))

    if req.tipo in ("cargo", "pessoa", "orgao"):
        gerar_pdf_agrupado(dados, elementos, styles['Normal'], group_by=req.tipo)
    else:
        gerar_pdf_agrupado(dados, elementos, styles['Normal'], group_by="flat")

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
    rows = core_busca_generica(
        tipo=req.tipo,
        busca=req.busca,
        ativo=req.ativo,
        mandato=req.mandato,
        sort_by=req.sort_by,
        session=session
    )

    # ========= 2) Monta o CSV ==========
    buffer = StringIO()
    writer = csv.writer(buffer)

    # Cabeçalho universal
    writer.writerow(["Pessoa", "Cargo", "Órgão", "Início", "Fim", "Mandato", "Observações"])

    if req.tipo == "flat":
        for r in rows:
            writer.writerow([
                r.get("pessoa", ""), r.get("cargo", ""), r.get("orgao", ""),
                r.get("data_inicio", "") or "", r.get("data_fim", "") or "", str(r.get("mandato", "")) if r.get("exclusivo", False) else "", r.get("observacoes", "") or ""
            ])
    else:
        if req.tipo == "cargo":
            for cargo in rows:
                chave = (cargo.get("cargo", ""), cargo.get("orgao", ""))
                ocupacoes = cargo.get("ocupacoes", [])
                for oc in ocupacoes:
                    writer.writerow([
                        oc.get("pessoa", ""),
                        chave[0],
                        chave[1],
                        oc.get("data_inicio", "") or "",
                        oc.get("data_fim", "") or "",
                        str(oc.get("mandato", "")) if oc.get("exclusivo", False) else "",
                        oc.get("observacoes", "") 
                    ])

        elif req.tipo == "pessoa":
            for pessoa in rows:
                chave = pessoa.get("pessoa", "")
                ocupacoes = pessoa.get("cargos", [])
                for oc in ocupacoes:
                    writer.writerow([
                        chave,
                        oc.get("cargo", ""),
                        oc.get("orgao", ""),
                        oc.get("data_inicio", "") or "",
                        oc.get("data_fim", "") or "",
                        str(oc.get("mandato", "")) if oc.get("exclusivo", False) else "",
                        oc.get("observacoes", "") 
                    ])

        elif req.tipo == "orgao":
            for orgao in rows:
                chave = orgao.get("orgao", "")
                ocupacoes = orgao.get("cargos", [])
                for oc in ocupacoes:
                    writer.writerow([
                        oc.get("pessoa", ""),
                        oc.get("cargo", ""),
                        chave,
                        oc.get("data_inicio", "") or "",
                        oc.get("data_fim", "") or "",
                        str(oc.get("mandato", "")) if oc.get("exclusivo", False) else "",
                        oc.get("observacoes", "") 
                    ])

    # ========= 3) Retorno como arquivo ==========
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=relatorio.csv"}
    )

