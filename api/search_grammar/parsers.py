from lark import Lark
from sqlmodel import case, select, and_, or_, not_

from models.pessoa import Pessoa
from models.cargo import Cargo
from models.orgao import Orgao
from models.ocupacao import Ocupacao
from search_grammar.grammar import grammar
from search_grammar.transformer import FiltroTransformer


# Exporta o transformer e parser para uso em outras partes do sistema
def parse_filtro(filtro, categoria_atual="pessoa"):
    parser = Lark(grammar, start="start")
    transformer = FiltroTransformer(categoria_atual=categoria_atual)
    tree = parser.parse(filtro)
    return transformer.transform(tree)

def traduzir_parsing_result(parse_result):
    """Traduz o dicionário lógico gerado pelo parser para expressões SQLAlchemy."""

    if "AND" in parse_result:
        return and_(*[traduzir_parsing_result(sub) for sub in parse_result["AND"]])
    elif "OR" in parse_result:
        return or_(*[traduzir_parsing_result(sub) for sub in parse_result["OR"]])
    elif "NOT" in parse_result:
        return not_(traduzir_parsing_result(parse_result["NOT"]))
    else:
        # Filtro simples

        if( "ELECTABLE TO" in parse_result):
            # Todas as pessoas que podem ser eleitas para o cargo X do órgão Y
            # Condição: Pessoas não são elegíveis se o o último mandato daquele cargo naquele órgão é delas e se este mandato é o segundo consecutivo.
            valor1 = parse_result["ELECTABLE TO"]["campo1"]
            valor2 = parse_result["ELECTABLE TO"]["campo2"]

            ultima_ocupacao = (
                select(Ocupacao.id_pessoa)
                .join(Cargo, Ocupacao.id_cargo == Cargo.id_cargo)
                .join(Orgao, Cargo.id_orgao == Orgao.id_orgao)
                .where(and_(Cargo.nome == valor1, Orgao.nome == valor2, Ocupacao.mandato >= 2, Pessoa.ativo == True))
                # data_fim nula significa vigente, então tratamos como "mais recente"
                .order_by(
                    case(
                        (Ocupacao.data_fim.is_(None), 1),  # os vigentes vêm primeiro
                        else_=0
                    ).desc(),
                    Ocupacao.data_fim.desc()               # senão, pega o mais recente
                )
                .limit(1)
            ).subquery()


            # Condição de inelegibilidade:
            # se o último mandato é dessa pessoa e é o segundo consecutivo
            condicao_ineligivel = Ocupacao.id_pessoa.in_(ultima_ocupacao)
    

            # Resultado final: quem é elegível
            return not_(condicao_ineligivel)

        campo = parse_result["campo"].lower()
        op = parse_result["op"]
        valor = parse_result["valor"]

        print("TRADUZINDO FILTRO:")
        print(campo, op, valor)
        if campo == "pessoa":
            coluna = Pessoa.nome
            print("Entrou em pessoa")
        elif campo == "cargo":
            coluna = Cargo.nome
        elif campo == "orgao":
            coluna = Orgao.nome
        elif campo == "inicio":
            coluna = Ocupacao.data_inicio
        elif campo == "fim":
            coluna = Ocupacao.data_fim
        elif campo == "mandato":
            coluna = Ocupacao.mandato
        else:
            raise ValueError(f"Campo desconhecido: {campo}")

        match op:
            case "=":
                print(valor)
                return coluna == valor
            
            case "LIKE":
                # *** CORREÇÃO AQUI: Implementação do LIKE usando ilike (case-insensitive) e curingas (%) ***
                if not isinstance(valor, str):
                    raise TypeError("O operador 'LIKE' só pode ser usado com valores de string.")
                
                print("AAAAAAAAA")
                return coluna.ilike(f"%{valor}%")
            
            case "<":
                return coluna < valor
            case ">":
                print("KSDJNKJFNSKN")
                return coluna > valor
            case _:
                raise ValueError(f"Operador inválido: {op}")
            

def traduzir_filtro_para_sql(filtro_str, categoria_atual="Pessoa"):
    parse_result = parse_filtro(filtro_str, categoria_atual=categoria_atual)
    print(parse_result)
    return traduzir_parsing_result(parse_result)