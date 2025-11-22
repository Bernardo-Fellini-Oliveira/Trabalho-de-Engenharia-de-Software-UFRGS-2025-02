import time
from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel
from database import get_connection # Presume-se que 'database' e 'get_connection' existem
from typing import List

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
def adicionar_lista_pessoas(pessoas: List[PessoaIn]):
    t0 = time.time()
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        ids_gerados = []
        
        # Iniciamos uma transação para garantir que ou salva tudo ou nada
        for p in pessoas:
            cursor.execute(
                "INSERT INTO Pessoa (nome, ativo) VALUES (%(nome)s, %(ativo)s)",
                {"nome": p.nome, "ativo": 1}
            )
            ids_gerados.append(cursor.lastrowid)
        
        conn.commit()
        
        tempo_total = time.time() - t0
        print(f"Tempo para adicionar {len(pessoas)} pessoas: {tempo_total:.4f}")

        return {
            "status": "success", 
            "message": f"{len(pessoas)} pessoas adicionadas com sucesso.", 
            "ids": ids_gerados
        }

    except Exception as e:
        if conn:
            conn.rollback() # Desfaz se der erro no meio
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar lista de Pessoas: {str(e)}")
    finally:
        if conn:
            conn.close()
    

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
                "UPDATE Pessoa SET ativo = 0 WHERE id_pessoa = %(id_pessoa)s AND ativo = 1",
                {"id_pessoa": id_pessoa}
            )
            
            if cursor.rowcount == 0:
                conn.close()
                raise HTTPException(status_code=404, detail=f"Pessoa com ID {id_pessoa} não encontrada ou já inativa.")
            
            conn.commit()
            conn.close()
            return {"status": "success", "message": f"Pessoa com ID {id_pessoa} inativada (soft delete) com sucesso."}
        
        else:
            # HARD DELETE (Exclusão permanente)
            cursor.execute("DELETE FROM Pessoa WHERE id_pessoa = %(id_pessoa)s", {"id_pessoa": id_pessoa})
            
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


@router.put("/reativar/{id_pessoa}")
def reativar_pessoa(id_pessoa: int = Path(..., description="ID da Pessoa a ser reativada")):
    """Reativa uma pessoa inativa pelo seu ID."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE Pessoa SET ativo = 1 WHERE id_pessoa = %(id_pessoa)s AND ativo = 0",
            {"id_pessoa": id_pessoa}
        )
        
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Pessoa com ID {id_pessoa} não encontrada ou já ativa.")
        
        conn.commit()
        conn.close()
        
        return {"status": "success", "message": f"Pessoa com ID {id_pessoa} reativada com sucesso."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao reativar Pessoa: {str(e)}")