from enum import Enum as PyEnum

#Enums de tipo de operação e entidades para o histórico
class TipoOperacao(str, PyEnum):
    ADICAO = "Adição"
    REMOCAO = "Remoção"
    INATIVACAO = "Inativação"
    REATIVACAO = "Reativação"
    ASSOCIACAO = "Associação"
    FINALIZACAO = "Finalização" 

class EntidadeAlvo(str, PyEnum):
    PESSOA = "Pessoa"
    ORGAO = "Órgão"
    CARGO = "Cargo"
    PORTARIA = "Portaria"
    OCUPACAO = "Ocupação"

class Status(str, PyEnum):
    PENDENTE = "Pendente"
    APROVADO = "Aprovado"
    RECUSADO = "Recusado"