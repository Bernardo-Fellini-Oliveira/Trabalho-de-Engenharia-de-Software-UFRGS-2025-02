import requests
import json

API_REMOVER_CARGO = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/remover/remover_cargo.php"
API_REMOVER_PORTARIA = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/remover/remover_portaria.php"
API_REMOVER_PESSOA = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/remover/remover_pessoa.php"
API_REMOVER_ORGAO = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/remover/remover_orgao.php"
API_REMOVER_OCUPACAO = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/remover/remover_ocupacao.php"




def remover_pessoa(id_pessoa):

    # Cria o payload (carga de dados) no formato que o PHP espera
    dados = {'id_pessoa': id_pessoa}
    
    try:
        # Faz a requisição POST, enviando os dados como JSON
        # A biblioteca 'requests' é inteligente e já define o Content-Type para application/json
        response = requests.post(API_REMOVER_PESSOA, json=dados)
        
        response.raise_for_status()
        
        print(f"Pessoa removida")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao salvar dados: {e}")
        return None




remover_pessoa(1)