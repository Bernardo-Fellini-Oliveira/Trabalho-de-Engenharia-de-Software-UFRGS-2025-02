from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel
from database import get_connection

router = APIRouter(    prefix="/api/ocupacao", # Define o prefixo aqui
                       tags=["Ocupação"])

class OcupacaoIn(BaseModel):
    """Modelo para adicionar uma nova Ocupação."""
    id_pessoa: int
    id_cargo: int
    id_portaria: int | None = None # Pode ser opcional (cargo sem mandado não precisa de portaria)
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

        # Regra 0: Data de início não pode ser posterior à data de fim
        if ocupacao.data_inicio and ocupacao.data_fim:
            if ocupacao.data_inicio > ocupacao.data_fim:
                raise HTTPException(status_code=400, detail="A data de início não pode ser posterior à data de fim.")

        # Regra 1: Impedir ocupação de cargo EXCLUSIVO iniciando em um período em que existe alguém o ocupando
        data_fim_novo = ocupacao.data_fim if ocupacao.data_fim is not None else '9999-12-31' 
        # 9999-12-31 representa uma data 'infinito' para mandatos em aberto

        cursor.execute(
            """
            SELECT id_ocupacao, id_pessoa 
            FROM Ocupacao JOIN Cargo ON Ocupacao.id_cargo = Cargo.id_cargo
            WHERE Cargo.exclusivo = 1 AND Ocupacao.id_cargo = %s AND 
            (
                -- Conflito: Ocupação existente (data_inicio) precede o NOVO FIM
                Ocupacao.data_inicio <= %s OR Ocupacao.data_inicio IS NULL 
                AND 
                -- E Ocupação existente (data_fim) sucede o NOVO INÍCIO
                (Ocupacao.data_fim IS NULL OR Ocupacao.data_fim >= %s)
            )
            """,
            # Parâmetros:
            (ocupacao.id_cargo, data_fim_novo, ocupacao.data_inicio) 
        )

        ocupacao_ativa = cursor.fetchone()
        print(ocupacao_ativa)
        if ocupacao_ativa:
            print("ALDAÇLS,DA,S")
            raise HTTPException(
                status_code=400,
                detail=f"O cargo {ocupacao.id_cargo} já está ocupado pela pessoa {ocupacao_ativa[1]}."
            )



        # Regra 2: verificar as últimas duas ocupações do mesmo cargo
        cursor.execute(
            """
            SELECT id_pessoa, id_ocupacao
            FROM Ocupacao
            WHERE id_cargo = %s
            ORDER BY data_fim DESC
            LIMIT 2
            """,
            (ocupacao.id_cargo,)
        )

        ultimas = [row[0] for row in cursor.fetchall()]

        print(ultimas)

        if len(ultimas) == 2 and all(pid == ocupacao.id_pessoa for pid in ultimas):
            raise HTTPException(
                status_code=400,
                detail="As últimas duas ocupações deste cargo já foram dessa mesma pessoa."
            )
        

        cursor.execute(
            """
            INSERT INTO Ocupacao 
            (id_pessoa, id_cargo, id_portaria, data_inicio, data_fim, mandato, observacoes) 
            VALUES (%(id_pessoa)s, %(id_cargo)s, %(id_portaria)s, %(data_inicio)s, %(data_fim)s, %(mandato)s, %(observacoes)s)
            """,
            {
                "id_pessoa": ocupacao.id_pessoa, 
                "id_cargo": ocupacao.id_cargo, 
                "id_portaria": ocupacao.id_portaria, 
                "data_inicio": ocupacao.data_inicio, 
                "data_fim": ocupacao.data_fim, 
                "mandato": ocupacao.mandato, 
                "observacoes": ocupacao.observacoes
            }
        )
        
        conn.commit()
        id_gerado = cursor.lastrowid
        conn.close()
        
        return {
            "status": "success", 
            "message": "Ocupação adicionada com sucesso", 
            "id_ocupacao": id_gerado
        }
    
    except HTTPException:
        raise

    except Exception as e:
        print("CCCCCCCCCCCCC")
        print(e)
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
        cursor.execute("DELETE FROM Ocupacao WHERE id_ocupacao = %(id_ocupacao)s", {"id_ocupacao": id_ocupacao})
        
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
    
@router.put("/finalizar/{id_ocupacao}")
def finalizar_ocupacao(id_ocupacao: int = Path(..., description="ID da Ocupação a ser finalizada")):
    """Finaliza um registro de ocupação pelo seu ID."""

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE Ocupacao
            SET data_fim = NOW()::date
            WHERE id_ocupacao = %(id_ocupacao)s
            """,
            {"id_ocupacao": id_ocupacao}
        )

        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Ocupação com ID {id_ocupacao} não encontrada")

        conn.commit()
        conn.close()

        return {"status": "success", "message": f"Ocupação com ID {id_ocupacao} finalizada com sucesso."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao finalizar Ocupação: {str(e)}")