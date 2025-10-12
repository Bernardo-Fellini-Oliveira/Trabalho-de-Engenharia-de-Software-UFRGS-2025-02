from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel
from database import get_connection

router = APIRouter(    prefix="/api/cargo", # Define o prefixo aqui
                       tags=["Cargo"])

class CargoIn(BaseModel):
    nome: str
    ativo: int
    id_orgao: int

@router.post("/")
def adicionar_cargo(cargo: CargoIn):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Cargo (nome, ativo, id_orgao) VALUES (?, ?, ?)",
            (cargo.nome, 1, cargo.id_orgao)
        )
        conn.commit()
        
        # Recupera o ID gerado
        id_gerado = cursor.lastrowid 
        
        conn.close()
        
        # Retorna o ID gerado
        return {"status": "success", "message": "Cargo adicionado com sucesso", "id_cargo": id_gerado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/")
def carregar_cargo():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Cargo")
        results = cursor.fetchall()
        conn.close()
        return [{"id_cargo": r[0], "nome": r[1], "ativo": r[2], "id_orgao": r[3]} for r in results]
    
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
                "UPDATE Cargo SET ativo = 0 WHERE id_cargo = ? AND ativo = 1", 
                (id_cargo,)
            )
            
            if cursor.rowcount == 0:
                conn.close()
                raise HTTPException(status_code=404, detail=f"Cargo com ID {id_cargo} não encontrado ou já inativo.")
            
            conn.commit()
            conn.close()
            return {"status": "success", "message": f"Cargo com ID {id_cargo} inativado (soft delete) com sucesso."}
        
        else:
            # HARD DELETE (Exclusão permanente)
            cursor.execute("DELETE FROM Cargo WHERE id_cargo = ?", (id_cargo,))
            
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