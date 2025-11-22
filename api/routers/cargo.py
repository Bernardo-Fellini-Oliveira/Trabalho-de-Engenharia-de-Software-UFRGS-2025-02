from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel
from database import get_connection
from typing import List

router = APIRouter(    prefix="/api/cargo", # Define o prefixo aqui
                       tags=["Cargo"])

class CargoIn(BaseModel):
    nome: str
    ativo: int
    id_orgao: int
    exclusivo: int | None = 1  # Novo campo, padrão 1 (exclusivo)

@router.post("/")
def adicionar_cargo(cargos: List[CargoIn]):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        for c in cargos:
            cursor.execute(
                "INSERT INTO Cargo (nome, ativo, id_orgao, exclusivo) VALUES (%(nome)s, %(ativo)s, %(id_orgao)s, %(exclusivo)s)",
                {"nome": c.nome, "ativo": 1, "id_orgao": c.id_orgao, "exclusivo": c.exclusivo}
            )
        conn.commit()
        
        
        conn.close()
        
        # Retorna o ID gerado
        return {"status": "success", "message": "Cargos adicionados com sucesso"}
    except Exception as e:
        if conn:
            conn.rollback() # Desfaz se der erro no meio
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar a lista de Cargos: {str(e)}")
    finally:
        if conn:
            conn.close()
    

@router.get("/")
def carregar_cargo():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Cargo")
        results = cursor.fetchall()
        conn.close()

        # Mapeia os resultados para uma lista de dicionários
        # 4 e 5 são created_at e updated_at, que não precisamos retornar
        return [{"id_cargo": r[0], "nome": r[1], "ativo": r[2], "id_orgao": r[3], "exclusivo": r[6]} for r in results]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.delete("/delete/{id_cargo}")
def remover_cargo(
    id_cargo: int = Path(..., description="ID do Cargo a ser removido"),
    soft: bool = Query(False, description="Se 'true', realiza soft delete (define ativo=0). Se 'false', realiza hard delete.")
):
    """Remove (ou inativa) um cargo pelo seu ID."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if soft:
            # AÇÃO DE SOFT DELETE (Define ativo=0)
            cursor.execute(
                "UPDATE Cargo SET ativo = 0 WHERE id_cargo = %(id_cargo)s AND ativo = 1", 
                {"id_cargo": id_cargo}
            )
            
            if cursor.rowcount == 0:
                conn.close()
                raise HTTPException(status_code=404, detail=f"Cargo com ID {id_cargo} não encontrado ou já inativo.")
            
            conn.commit()
            conn.close()
            return {"status": "success", "message": f"Cargo com ID {id_cargo} inativado (soft delete) com sucesso."}
        
        else:
            # HARD DELETE (Exclusão permanente)
            cursor.execute("DELETE FROM Cargo WHERE id_cargo = %(id_cargo)s", {"id_cargo": id_cargo})
            
            if cursor.rowcount == 0:
                conn.close()
                raise HTTPException(status_code=404, detail=f"Cargo com ID {id_cargo} não encontrado")

            conn.commit()
            conn.close()
            
            return {"status": "success", "message": f"Cargo com ID {id_cargo} removido permanentemente (hard delete) com sucesso."}
            
    except HTTPException:
        raise
    except Exception as e:
        # Captura erros como violação de chave estrangeira
        raise HTTPException(status_code=500, detail=f"Erro ao remover Cargo: {str(e)}. Verifique se há ocupações vinculadas.")
    

@router.put("/reativar/{id_cargo}")
def reativar_cargo(id_cargo: int = Path(..., description="ID do Cargo a ser reativado")):
    """Reativa um cargo inativo pelo seu ID."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE Cargo SET ativo = 1 WHERE id_cargo = %(id_cargo)s AND ativo = 0",
            {"id_cargo": id_cargo}
        )
        
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Cargo com ID {id_cargo} não encontrado ou já ativo.")
        
        conn.commit()
        conn.close()
        
        return {"status": "success", "message": f"Cargo com ID {id_cargo} reativado com sucesso."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))