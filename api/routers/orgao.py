from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel
from database import get_connection

router = APIRouter(    prefix="/api/orgao", # Define o prefixo aqui
                       tags=["Órgão"])

class OrgaoIn(BaseModel):
    nome: str
    ativo: int

@router.post("/")
def adicionar_orgao(orgao: OrgaoIn):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # O id_orgao é autoincrementado, não incluímos ele na inserção
        cursor.execute(
            "INSERT INTO Orgao (nome, ativo) VALUES (%(nome)s, %(ativo)s)",
            {"nome": orgao.nome, "ativo": 1}
        )
        
        conn.commit()
        
        # >>> AQUI: Recupera o ID gerado pelo AUTOINCREMENT <<<
        id_gerado = cursor.lastrowid
        
        conn.close()
        
        # Retorna o ID gerado
        return {"status": "success", "message": "Órgão adicionado com sucesso", "id_orgao": id_gerado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar Órgão: {str(e)}")
    
@router.get("/")
def carregar_orgao():
    """Carrega todos os órgãos do banco de dados."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id_orgao, nome, ativo FROM Orgao")
        results = cursor.fetchall()
        
        conn.close()
        
        # Mapeia os resultados para uma lista de dicionários
        return [{"id_orgao": r[0], "nome": r[1], "ativo": r[2]} for r in results]
    except Exception as e:
        # Lidar com erros de conexão ou SQL
        raise HTTPException(status_code=500, detail=f"Erro ao carregar Órgãos: {str(e)}")
    

@router.delete("/delete/{id_orgao}")
def remover_orgao(
    id_orgao: int = Path(..., description="ID do Órgão a ser removido"),
    soft: bool = Query(False, description="Se 'true', realiza soft delete (define ativo=0). Se 'false', realiza hard delete.")
):
    """Remove (ou inativa) um órgão pelo seu ID."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if soft:
            # AÇÃO DE SOFT DELETE (Define ativo=0)
            cursor.execute(
                "UPDATE Orgao SET ativo = 0 WHERE id_orgao = %(id_orgao)s AND ativo = 1", 
                {"id_orgao": id_orgao}
            )
            
            if cursor.rowcount == 0:
                conn.close()
                raise HTTPException(status_code=404, detail=f"Órgão com ID {id_orgao} não encontrado ou já inativo.")
            
            conn.commit()
            conn.close()
            return {"status": "success", "message": f"Órgão com ID {id_orgao} inativado (soft delete) com sucesso."}
        
        else:
            # HARD DELETE (Exclusão permanente)
            cursor.execute("DELETE FROM Orgao WHERE id_orgao = %(id_orgao)s", {"id_orgao": id_orgao})
            
            if cursor.rowcount == 0:
                conn.close()
                raise HTTPException(status_code=404, detail=f"Órgão com ID {id_orgao} não encontrado")

            conn.commit()
            conn.close()
            
            return {"status": "success", "message": f"Órgão com ID {id_orgao} removido permanentemente (hard delete) com sucesso."}
            
    except HTTPException:
        raise
    except Exception as e:
        # Captura erros como violação de chave estrangeira
        raise HTTPException(status_code=500, detail=f"Erro ao remover Órgão: {str(e)}. Verifique se há cargos vinculados.")
    
@router.put("/reativar/{id_orgao}")
def reativar_orgao(id_orgao: int = Path(..., description="ID do Órgão a ser reativado")):
        """Reativa um órgão inativo pelo seu ID."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE Orgao SET ativo = 1 WHERE id_orgao = %(id_orgao)s AND ativo = 0",
                {"id_orgao": id_orgao}
            )
            
            if cursor.rowcount == 0:
                conn.close()
                raise HTTPException(status_code=404, detail=f"Órgão com ID {id_orgao} não encontrado ou já ativo.")
            
            conn.commit()
            conn.close()
            
            return {"status": "success", "message": f"Órgão com ID {id_orgao} reativado com sucesso."}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao reativar Órgão: {str(e)}")