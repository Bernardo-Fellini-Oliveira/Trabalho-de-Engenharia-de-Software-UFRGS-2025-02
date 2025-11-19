grammar = r"""
?start: expr

?expr: expr "OR" term   -> or_expr
     | expr "AND" term  -> and_expr
     | term

?term: "NOT" term       -> not_expr
     | expr    
     | "(" expr ")"     -> grouped
     | filtro      

filtro: campo_string OP_STRING valor_str  -> filtro_term_string
     |  campo_numeric OP_NUMERIC valor_int           -> filtro_term_numeric
     |  campo_date OP_DATE valor_str            -> filtro_term_date
     |  "ELECTABLE TO" valor_str "DE" valor_str           -> filtro_electable_to
     |  valor_str                           -> filtro_str_simplified

campo_string: "Pessoa"       -> pessoa
              | "Cargo"      -> cargo
              | "Orgao"      -> orgao

campo_numeric: "Mandato"  -> mandato

campo_date: "Inicio"   -> inicio
            | "Fim"   -> fim

OP_NUMERIC: "=" | "<" | ">"
OP_STRING: "=" | "LIKE"
OP_DATE: "=" | "<" | ">" 

valor_str: ESCAPED_STRING   -> string
valor_int: INT               -> int

%import common.ESCAPED_STRING
%import common.INT
%import common.WS
%ignore WS
"""



