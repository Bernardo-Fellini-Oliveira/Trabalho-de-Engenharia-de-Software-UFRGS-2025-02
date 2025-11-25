import datetime
from lark import Transformer, v_args

"""

@v_args(inline=True) decorator is part of the Lark library, which is used for parsing and transforming grammars. This decorator modifies how arguments are passed to methods in a Transformer class when processing parse trees.

Explanation
When inline=True is used, the children of a node in the parse tree are passed as individual arguments to the method, instead of being passed as a list.
This can make the code cleaner and more intuitive when the number of children is fixed and known.

"""
@v_args(inline=True)
class FiltroTransformer(Transformer):
    def __init__(self, categoria_atual="pessoa"):
        super().__init__()
        self.categoria_atual = categoria_atual.lower()

    def string(self, s):
        return s[1:-1]  # remove aspas
    
    def int(self, n):
        return int(n)
    
    def filtro_term_string(self, campo, op, valor):
        return {"campo": str(campo), "op": str(op), "valor": valor}
    
    def filtro_term_numeric(self, campo, op, valor):
        return {"campo": str(campo), "op": str(op), "valor": int(valor)}
    
    def filtro_electable_to(self, valor1, valor2):
        return {"ELECTABLE TO": {"campo1": valor1, "campo2": valor2}}
    
    def filtro_str_simplified(self, valor):
        return {"campo": self.categoria_atual, "op": "LIKE", "valor": valor}
    
    def filtro_term_date(self, campo, op, valor):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return {"campo": str(campo), "op": str(op), "valor": datetime.datetime.strptime(valor, fmt).date()}
            except ValueError:
                continue
        raise ValueError(f"Formato de data inválido: {valor}")

    def and_expr(self, e1, e2):
        return {"AND": [e1, e2]}
    
    def or_expr(self, e1, e2):
        return {"OR": [e1, e2]}
    
    def not_expr(self, e):
        return {"NOT": e}
    
    def grouped(self, e):
        return e
    
    def not_grouped_expr(self, e):
        return e
    
    def campo_string(self, token):
        return str(token)
    
    def campo_numeric(self, token):
        return str(token)
    
    def campo_date(self, token):
        return str(token)
    
