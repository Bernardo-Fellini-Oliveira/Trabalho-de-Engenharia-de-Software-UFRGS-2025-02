import requests
import json

API_CARREGAR_CARGO = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/carregar/carregar_cargo.php"
API_CARREGAR_PORTARIA = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/carregar/carregar_portaria.php"
API_CARREGAR_PESSOA = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/carregar/carregar_pessoa.php"
API_CARREGAR_ORGAO = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/carregar/carregar_orgao.php"
API_CARREGAR_OCUPACAO = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/carregar/carregar_ocupacao.php"


API_CRIA_CARGO = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/adicionar/adicionar_cargo.php"
API_CRIA_PORTARIA = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/adicionar/adicionar_portaria.php"
API_CRIA_PESSOA = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/adicionar/adicionar_pessoa.php"
API_CRIA_ORGAO = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/adicionar/adicionar_orgao.php"
API_CRIA_OCUPACAO = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/adicionar/adicionar_ocupacao.php"


def cria_pessoa(id_pessoa, nome):

    # Cria o payload (carga de dados) no formato que o PHP espera
    dados = {'id_pessoa': id_pessoa, 'nome': nome}
    
    try:
        # Faz a requisição POST, enviando os dados como JSON
        # A biblioteca 'requests' é inteligente e já define o Content-Type para application/json
        response = requests.post(API_CRIA_PESSOA, json=dados)
        
        response.raise_for_status()
        
        print(f"Pessoa adicionada")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao salvar dados: {e}")
        return None


def cria_orgao(id_orgao, nome, ativo):

    # Cria o payload (carga de dados) no formato que o PHP espera
    dados = {'id_orgao': id_orgao, 'nome': nome, 'ativo': ativo}
    
    try:
        # Faz a requisição POST, enviando os dados como JSON
        # A biblioteca 'requests' é inteligente e já define o Content-Type para application/json
        response = requests.post(API_CRIA_ORGAO, json=dados)
        
        response.raise_for_status()
        
        print(f"Orgao adicionada")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao salvar dados: {e}")
        return None

def cria_cargo(id_cargo, nome, ativo, id_orgao):

    # Cria o payload (carga de dados) no formato que o PHP espera
    dados = {'id_cargo': id_cargo, 'nome': nome, 'ativo': ativo, 'id_orgao':id_orgao}
    
    try:
        # Faz a requisição POST, enviando os dados como JSON
        # A biblioteca 'requests' é inteligente e já define o Content-Type para application/json
        response = requests.post(API_CRIA_CARGO, json=dados)
        
        response.raise_for_status()
        
        print(f"Cargo adicionada")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao salvar dados: {e}")
        return None
    
def cria_portaria(id_portaria, numero, data, observacoes):

    # Cria o payload (carga de dados) no formato que o PHP espera
    dados = {'id_portaria': id_portaria, 'numero': numero, 'data': data, 'observacoes':observacoes}
    
    try:
        # Faz a requisição POST, enviando os dados como JSON
        # A biblioteca 'requests' é inteligente e já define o Content-Type para application/json
        response = requests.post(API_CRIA_PORTARIA, json=dados)
        
        response.raise_for_status()
        
        print(f"Portaria adicionada")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao salvar dados: {e}")
        return None

def cria_ocupacao(id_ocupacao, id_pessoa, id_cargo, id_portaria, data_inicio, data_fim, mandato, observacoes):

    # Cria o payload (carga de dados) no formato que o PHP espera
    dados = {'id_ocupacao': id_ocupacao, 'id_pessoa': id_pessoa, 'id_cargo': id_cargo, 'id_portaria':id_portaria, 'data_inicio':data_inicio, 'data_fim':data_fim, 'mandato':mandato, 'observacoes':observacoes}
    
    try:
        # Faz a requisição POST, enviando os dados como JSON
        # A biblioteca 'requests' é inteligente e já define o Content-Type para application/json
        response = requests.post(API_CRIA_OCUPACAO, json=dados)
        
        response.raise_for_status()
        
        print(f"Ocupacao adicionada")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao salvar dados: {e}")
        return None


cria_pessoa(1, "luciano")