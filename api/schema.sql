CREATE TABLE IF NOT EXISTS Pessoa (
    id_pessoa SERIAL PRIMARY KEY, 
    nome TEXT NOT NULL,
    ativo BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Orgao (
    id_orgao SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    ativo BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Cargo (
    id_cargo SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    ativo BOOLEAN NOT NULL,
    id_orgao INTEGER REFERENCES Orgao (id_orgao),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exclusivo BOOLEAN DEFAULT TRUE

);

CREATE TABLE IF NOT EXISTS Portaria (
    id_portaria SERIAL PRIMARY KEY,
    numero INTEGER NOT NULL,
    data_portaria TEXT NOT NULL,
    observacoes TEXT,
    ativo BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Ocupacao (
    id_ocupacao SERIAL PRIMARY KEY,
    id_pessoa INTEGER REFERENCES Pessoa (id_pessoa) NOT NULL,
    id_cargo INTEGER REFERENCES Cargo (id_cargo) NOT NULL,
    id_portaria INTEGER REFERENCES Portaria (id_portaria),
    data_inicio TIMESTAMP,
    data_fim TIMESTAMP,
    mandato INTEGER NOT NULL,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Historico (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo_operacao TEXT NOT NULL,
    entidade_alvo TEXT NOT NULL,
    operation TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Notificacoes (
    id SERIAL PRIMARY KEY,
    data_solicitacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    operation TEXT NOT NULL,
    dados_payload JSON NOT NULL,
    tipo_operacao TEXT NOT NULL,
    entidade_alvo TEXT NOT NULL,
    status_aprovacao TEXT NOT NULL DEFAULT 'Pendente',
    data_aprovacao TIMESTAMP,
    aprovador_id INTEGER
);


CREATE OR REPLACE FUNCTION atualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;



CREATE TRIGGER update_portaria_timestamp
BEFORE UPDATE ON Portaria
FOR EACH ROW
EXECUTE FUNCTION atualizar_timestamp();

------------------------

CREATE TRIGGER update_pessoa_timestamp
BEFORE UPDATE ON Pessoa
FOR EACH ROW
EXECUTE FUNCTION atualizar_timestamp();

-----------------------

CREATE TRIGGER update_orgao_timestamp
BEFORE UPDATE ON Orgao
FOR EACH ROW
EXECUTE FUNCTION atualizar_timestamp();

-----------------------

CREATE TRIGGER update_cargo_timestamp
BEFORE UPDATE ON Cargo
FOR EACH ROW
EXECUTE FUNCTION atualizar_timestamp();

-----------------------

CREATE TRIGGER update_ocupacao_timestamp
BEFORE UPDATE ON Ocupacao
FOR EACH ROW
EXECUTE FUNCTION atualizar_timestamp();

-----------------------

CREATE TRIGGER update_historico_timestamp
BEFORE UPDATE ON Historico
FOR EACH ROW
EXECUTE FUNCTION atualizar_timestamp();

-----------------------

CREATE TRIGGER update_notificacoes_timestamp
BEFORE UPDATE ON Historico
FOR EACH ROW
EXECUTE FUNCTION atualizar_timestamp();