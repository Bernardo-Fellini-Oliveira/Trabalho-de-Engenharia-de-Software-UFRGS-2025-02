# Trabalho-de-Engenharia-de-Software-UFRGS-2025-02

Leitura:
 - API_CARREGAR_CARGO = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/carregar/carregar_cargo.php"
 - API_CARREGAR_PORTARIA = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/carregar/carregar_portaria.php"
 - API_CARREGAR_PESSOA = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/carregar/carregar_pessoa.php"
 - API_CARREGAR_ORGAO = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/carregar/carregar_orgao.php"
 - API_CARREGAR_OCUPACAO = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/carregar/carregar_ocupacao.php"

Escrita
 - API_CRIA_CARGO = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/adicionar/adicionar_cargo.php"
 - API_CRIA_PORTARIA = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/adicionar/adicionar_portaria.php"
 - API_CRIA_PESSOA = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/adicionar/adicionar_pessoa.php"
 - API_CRIA_ORGAO = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/adicionar/adicionar_orgao.php"
 - API_CRIA_OCUPACAO = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/adicionar/adicionar_ocupacao.php"

 Remover:
 - API_REMOVER_CARGO = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/remover/remover_cargo.php"
 - API_REMOVER_PORTARIA = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/remover/remover_portaria.php"
 - API_REMOVER_PESSOA = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/remover/remover_pessoa.php"
 - API_REMOVER_ORGAO = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/remover/remover_orgao.php"
 - API_REMOVER_OCUPACAO = "https://www.inf.ufrgs.br/~ikscarvalho/eng-software/remover/remover_ocupacao.php"


 SQL:
 CREATE TABLE Pessoa
(
	id_pessoa INTEGER PRIMARY KEY,
	nome TEXT NOT NULL
);

CREATE TABLE Orgao
(
	id_orgao INTEGER PRIMARY KEY,
	nome TEXT NOT NULL,
	ativo INTEGER NOT NULL --SQLite nao tem bool
);

CREATE TABLE Cargo
(
	id_cargo INTEGER PRIMARY KEY,
	nome TEXT NOT NULL,
	ativo INTEGER NOT NULL,
	id_orgao INTEGER REFERENCES Orgao (id_orgao)
);

CREATE TABLE Portaria
(
	id_portaria INTEGER PRIMARY KEY,
	numero INTEGER NOT NULL,
	data TEXT NOT NULL, --SQlite nao tem tipo datetime
	observacoes TEXT
);

CREATE TABLE Ocupacao
(
	id_ocupacao INTEGER PRIMARY KEY,
	id_pessoa INTEGER REFERENCES Pessoa (id_pessoa) NOT NULL,
	id_cargo INTEGER REFERENCES Cargo (id_cargo) NOT NULL,
	id_portaria INTEGER REFERENCES Portaria (id_portaria),
	data_inicio TEXT,
	data_fim TEXT,
	mandato INTEGER NOT NULL,
	observacoes TEXT
);