from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, and_, select

from routers.ocupacao import _get_next_occupacao, _get_prev_occupacao
from models.cargo import Cargo
from models.ocupacao import Ocupacao
from models.pessoa import Pessoa
from database import get_session

class RegraViolada:
    OCUPACAO_EXISTENTE = 1
    TERCEIRO_MANDATO = 2


class ElegibilidadeResultado:
    def __init__(self, elegivel, regra=None, detalhe=None, ocupacao_conflitante=None):
        self.elegivel = elegivel
        self.regra = regra
        self.detalhe = detalhe
        self.ocupacao_conflitante = ocupacao_conflitante

    def to_dict(self):
        return {
            "elegivel": self.elegivel,
            "regra": self.regra,
            "detalhe": self.detalhe,
            "ocupacao_conflitante": self.ocupacao_conflitante,
        }


router = APIRouter(
    prefix="/api/elegibilidade",
    tags=["Elegibilidade"],
    responses={404: {"description": "router problem"}},
)


def verificar_regra_cargo_exclusivo(session: Session, id_cargo: int, data_inicio, data_fim):
    cargo = session.get(Cargo, id_cargo)
    if not cargo or not cargo.exclusivo:
        return None   # regra não se aplica

    data_inicio_nova = data_inicio or date.min

    ocupacao_existente = session.exec(
        select(Ocupacao).where(
            and_(
                Ocupacao.id_cargo == id_cargo,
                ((Ocupacao.data_inicio == None)),
                ((Ocupacao.data_fim == None) | (Ocupacao.data_fim >= data_inicio_nova)),
            )
        )
    ).first()

    if ocupacao_existente:
        pessoa = session.get(Pessoa, ocupacao_existente.id_pessoa)
        return ElegibilidadeResultado(
            elegivel=False,
            regra=RegraViolada.OCUPACAO_EXISTENTE,
            detalhe=f"Cargo já está ocupado por {pessoa.nome}.",
            ocupacao_conflitante=ocupacao_existente.id_ocupacao
        )

    return None



def verificar_regra_terceiro_mandato(session: Session, id_pessoa, id_cargo, data_inicio):

    anterior = _get_prev_occupacao(session, id_cargo, data_inicio or date.min)
    proxima = _get_next_occupacao(session, id_cargo, data_inicio or date.min)

    num_seguidos = 1

    if anterior and anterior.id_pessoa == id_pessoa:
        num_seguidos = (anterior.mandato or 0) + 1

    contador = num_seguidos
    atual = proxima

    while atual and atual.id_pessoa == id_pessoa:
        contador += 1
        atual = _get_next_occupacao(
            session, atual.id_cargo, atual.data_inicio or date.min, atual.id_ocupacao
        )

    if contador > 2:
        pessoa = session.get(Pessoa, id_pessoa)
        cargo = session.get(Cargo, id_cargo)
        return ElegibilidadeResultado(
            elegivel=False,
            regra=RegraViolada.TERCEIRO_MANDATO,
            detalhe=f"{pessoa.nome} já possui duas ocupações consecutivas no cargo {cargo.nome}.",
        )

    return None


def verificar_elegibilidade(session: Session, id_pessoa: int, id_cargo: int, data_inicio, data_fim=None):
    # Regra 1 — cargo ocupado
    regra1 = verificar_regra_cargo_exclusivo(session, id_cargo, data_inicio, data_fim)
    if regra1:
        return regra1

    # Regra 2 — terceiro mandato
    regra2 = verificar_regra_terceiro_mandato(session, id_pessoa, id_cargo, data_inicio)
    if regra2:
        return regra2

    # Todas as regras foram atendidas
    return ElegibilidadeResultado(elegivel=True)


@router.get("/verificar_elegibilidade/")
def verificar_elegibilidade_endpoint(
    id_pessoa: int = Query(..., description="ID da Pessoa a ser verificada"),
    id_cargo: int = Query(..., description="ID do Cargo a ser verificado"),
    data_inicio: date = Query(..., description="Data de início da ocupação"),
    data_fim: date | None = Query(None, description="Data de fim da ocupação"),
    session: Session = Depends(get_session)
):
    resultado = verificar_elegibilidade(session, id_pessoa, id_cargo, data_inicio, data_fim)
    return resultado.to_dict()
    


