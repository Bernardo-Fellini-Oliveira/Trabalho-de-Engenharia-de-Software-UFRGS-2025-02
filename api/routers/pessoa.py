import time
from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel
from database import get_connection # Presume-se que 'database' e 'get_connection' existem

router = APIRouter(    prefix="/api/pessoa", # Define o prefixo aqui
                       tags=["Pessoa"])

@router.get("/")
def carregar_pessoa():
    """Carrega todas as pessoas do banco de dados."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id_pessoa, nome, ativo FROM Pessoa")
        results = cursor.fetchall()
        
        conn.close()
        
        # Mapeia os resultados para uma lista de dicionários
        return [{"id_pessoa": r[0], "nome": r[1], "ativo": r[2]} for r in results]
    except Exception as e:
        # Lidar com erros de conexão ou SQL
        raise HTTPException(status_code=500, detail=f"Erro ao carregar Pessoas: {str(e)}")
    

class PessoaIn(BaseModel):
    nome: str

@router.post("/")
def adicionar_pessoa(pessoa: PessoaIn):
    t0 = time.time()
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # O id_pessoa é autoincrementado, não incluímos ele na inserção
        cursor.execute(
            "INSERT INTO Pessoa (nome, ativo) VALUES (?, ?)",
            (pessoa.nome, 1)
        )
        
        conn.commit()
        
        # >>> AQUI: Recupera o ID gerado pelo AUTOINCREMENT <<<
        id_gerado = cursor.lastrowid
        
        conn.close()

        print(f"Tempo para adicionar pessoa: {time.time() - t0:.4f}")

        # Retorna o ID gerado
        return {"status": "success", "message": "Pessoa adicionada com sucesso", "id_pessoa": id_gerado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar Pessoa: {str(e)}")
    

@router.delete("/delete/{id_pessoa}")
def remover_pessoa(
    id_pessoa: int = Path(..., description="ID da Pessoa a ser removida"),
    soft: bool = Query(False, description="Se 'true', realiza soft delete (define ativo=0). Se 'false', realiza hard delete.")
):
    """Remove (ou inativa) uma pessoa pelo seu ID."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if soft:
            # AÇÃO DE SOFT DELETE (Define ativo=0)
            cursor.execute(
                "UPDATE Pessoa SET ativo = 0 WHERE id_pessoa = ? AND ativo = 1", 
                (id_pessoa,)
            )
            
            if cursor.rowcount == 0:
                conn.close()
                raise HTTPException(status_code=404, detail=f"Pessoa com ID {id_pessoa} não encontrada ou já inativa.")
            
            conn.commit()
            conn.close()
            return {"status": "success", "message": f"Pessoa com ID {id_pessoa} inativada (soft delete) com sucesso."}
        
        else:
            # HARD DELETE (Exclusão permanente)
            cursor.execute("DELETE FROM Pessoa WHERE id_pessoa = ?", (id_pessoa,))
            
            if cursor.rowcount == 0:
                conn.close()
                raise HTTPException(status_code=404, detail=f"Pessoa com ID {id_pessoa} não encontrada.")

            conn.commit()
            conn.close()
            
            return {"status": "success", "message": f"Pessoa com ID {id_pessoa} removida permanentemente (hard delete) com sucesso."}
            
    except HTTPException:
        raise
    except Exception as e:
        # Captura erros como violação de chave estrangeira
        raise HTTPException(status_code=500, detail=f"Erro ao remover Pessoa: {str(e)}. Verifique se há vínculos (Ocupações) ativos.")


