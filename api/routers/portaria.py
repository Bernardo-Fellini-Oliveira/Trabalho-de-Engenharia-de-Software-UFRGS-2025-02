from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel
from database import get_connection

router = APIRouter(    prefix="/api/portaria", # Define o prefixo aqui
                       tags=["Portaria"])


class PortariaIn(BaseModel):
    """Modelo para adicionar uma nova Portaria."""
    numero: int
    data_portaria: str  # Sugestão: usar formato 'YYYY-MM-DD'
    observacoes: str | None # Campo opcional
    ativo: int | None = 1


@router.get("/")
def carregar_portaria():
    """Carrega todas as portarias do banco de dados."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id_portaria, numero, data_portaria, observacoes, ativo FROM Portaria")
        results = cursor.fetchall()
        
        conn.close()
        
        # Mapeia os resultados para uma lista de dicionários

        return [
            {
                "id_portaria": r[0], 
                "numero": r[1], 
                "data_portaria": r[2], 
                "observacoes": r[3],
                "ativo": r[4]
            } 
            for r in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar Portarias: {str(e)}")
    

@router.post("/")
def adicionar_portaria(portaria: PortariaIn):
    """Adiciona uma nova portaria ao banco de dados e retorna o ID gerado."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # O id_portaria é AUTOINCREMENTADO, não precisa ser incluído no INSERT.
        cursor.execute(
            "INSERT INTO Portaria (numero, data_portaria, observacoes, ativo) VALUES (?, ?, ?, ?)",
            (portaria.numero, portaria.data_portaria, portaria.observacoes, 1)
        )

        conn.commit()
        id_gerado = cursor.lastrowid
        conn.close()
        
        return {
            "status": "success", 
            "message": "Portaria adicionada com sucesso", 
            "id_portaria": id_gerado
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar Portaria: {str(e)}")


@router.delete("/delete/{id_portaria}")
def remover_portaria(id_portaria: int = Path(..., description="ID da Portaria a ser removida"),
                    soft: bool = Query(False, description="Se 'true', realiza soft delete (define ativo=0). Se 'false', realiza hard delete.")):
    
    """Remove uma portaria (ou inativa) pelo seu ID."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if soft:
            # AÇÃO DE SOFT DELETE (Define ativo=0)
            cursor.execute(
                "UPDATE Portaria SET ativo = 0 WHERE id_portaria = ? AND ativo = 1",
                (id_portaria,)
            )

            if cursor.rowcount == 0:
                conn.close()
                raise HTTPException(status_code=404, detail=f"Portaria com ID {id_portaria} não encontrada ou já inativa.")

            conn.commit()
            conn.close()
            return {"status": "success", "message": f"Portaria com ID {id_portaria} inativada (soft delete) com sucesso."}

        else:
            # HARD DELETE (Exclusão permanente)
            cursor.execute("DELETE FROM Portaria WHERE id_portaria = ?", (id_portaria,))

            if cursor.rowcount == 0:
                conn.close()
                raise HTTPException(status_code=404, detail=f"Portaria com ID {id_portaria} não encontrada.")

            conn.commit()
            conn.close()
        
            return {"status": "success", "message": f"Portaria com ID {id_portaria} removida com sucesso."}
        
    except HTTPException:
        raise
    except Exception as e:
        # Captura erros como violação de chave estrangeira (se houver Ocupações ligadas a esta Portaria)
        raise HTTPException(status_code=500, detail=f"Erro ao remover Portaria: {str(e)}. Verifique se há ocupações vinculadas.")


