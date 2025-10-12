from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel
from database import get_connection

router = APIRouter(    prefix="/api/ocupacao", # Define o prefixo aqui
                       tags=["Ocupação"])

class OcupacaoIn(BaseModel):
    """Modelo para adicionar uma nova Ocupação."""
    id_pessoa: int
    id_cargo: int
    id_portaria: int | None = None # Pode ser opcional, dependendo da regra de negócio
    data_inicio: str | None = None # Sugestão: formato 'YYYY-MM-DD'
    data_fim: str | None = None
    mandato: int 
    observacoes: str | None = None

@router.post("/")
def adicionar_ocupacao(ocupacao: OcupacaoIn):
    """Adiciona uma nova ocupação ao banco de dados e retorna o ID gerado."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # O id_ocupacao é AUTOINCREMENTADO
        cursor.execute(
            """
            INSERT INTO Ocupacao 
            (id_pessoa, id_cargo, id_portaria, data_inicio, data_fim, mandato, observacoes) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ocupacao.id_pessoa, 
                ocupacao.id_cargo, 
                ocupacao.id_portaria, 
                ocupacao.data_inicio, 
                ocupacao.data_fim, 
                ocupacao.mandato, 
                ocupacao.observacoes
            )
        )
        
        conn.commit()
        id_gerado = cursor.lastrowid
        conn.close()
        
        return {
            "status": "success", 
            "message": "Ocupação adicionada com sucesso", 
            "id_ocupacao": id_gerado
        }
    except Exception as e:
        # Erros comuns: Foreign Key Constraint (id_pessoa, id_cargo, id_portaria inexistentes)
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar Ocupação. Verifique se os IDs de Pessoa, Cargo e Portaria existem: {str(e)}")




@router.get("/")
def carregar_ocupacao():
    """Carrega todas as ocupações do banco de dados."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id_ocupacao, id_pessoa, id_cargo, id_portaria, data_inicio, data_fim, mandato, observacoes 
            FROM Ocupacao
            """
        )
        results = cursor.fetchall()
        
        conn.close()
        
        # Mapeia os resultados para uma lista de dicionários
        return [
            {
                "id_ocupacao": r[0], 
                "id_pessoa": r[1], 
                "id_cargo": r[2], 
                "id_portaria": r[3], 
                "data_inicio": r[4], 
                "data_fim": r[5], 
                "mandato": r[6], 
                "observacoes": r[7]
            } 
            for r in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar Ocupações: {str(e)}")
    


@router.delete("/delete/{id_ocupacao}")
def remover_ocupacao(id_ocupacao: int = Path(..., description="ID da Ocupação a ser removida")):
    """Remove um registro de ocupação pelo seu ID."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 1. Tenta remover a ocupação
        cursor.execute("DELETE FROM Ocupacao WHERE id_ocupacao = ?", (id_ocupacao,))
        
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Ocupação com ID {id_ocupacao} não encontrada")

        conn.commit()
        conn.close()
        
        return {"status": "success", "message": f"Ocupação com ID {id_ocupacao} removida com sucesso."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover Ocupação: {str(e)}")