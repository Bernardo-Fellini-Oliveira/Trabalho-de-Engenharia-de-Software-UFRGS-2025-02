--Caso queira recriar o banco de dados, execute este script SQL para apagar as tabelas e sequências existentes e criar novas.

DROP FUNCTION IF EXISTS atualizar_timestamp CASCADE;
DROP SEQUENCE IF EXISTS Pessoa_id_pessoa_seq CASCADE;
DROP SEQUENCE IF EXISTS Orgao_id_orgao_seq CASCADE;
DROP SEQUENCE IF EXISTS Cargo_id_cargo_seq CASCADE;
DROP SEQUENCE IF EXISTS Portaria_id_portaria_seq CASCADE;
DROP SEQUENCE IF EXISTS Ocupacao_id_ocupacao_seq CASCADE;
DROP SEQUENCE IF EXISTS Usuario_id_user_seq CASCADE;


CREATE TABLE IF NOT EXISTS Pessoa (
    id_pessoa SERIAL PRIMARY KEY, 
    nome TEXT NOT NULL,
    ativo BOOLEAN NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (nome)
);

CREATE TABLE IF NOT EXISTS Orgao (
    id_orgao SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    ativo BOOLEAN NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (nome)
);

CREATE TABLE IF NOT EXISTS Cargo (
    id_cargo SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    ativo BOOLEAN NOT NULL,
    id_orgao INTEGER REFERENCES Orgao (id_orgao),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    exclusivo BOOLEAN DEFAULT TRUE,
    substituto_para INTEGER REFERENCES Cargo (id_cargo),
    substituto INTEGER REFERENCES Cargo (id_cargo),
    UNIQUE (nome, id_orgao)

);

CREATE TABLE IF NOT EXISTS Portaria (
    id_portaria SERIAL PRIMARY KEY,
    numero INTEGER NOT NULL,
    data_portaria TEXT NOT NULL,
    observacoes TEXT,
    ativo BOOLEAN NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (numero, data_portaria)
);

CREATE TABLE IF NOT EXISTS Ocupacao (
    id_ocupacao SERIAL PRIMARY KEY,
    id_pessoa INTEGER REFERENCES Pessoa (id_pessoa) NOT NULL,
    id_cargo INTEGER REFERENCES Cargo (id_cargo) NOT NULL,
    id_portaria INTEGER REFERENCES Portaria (id_portaria),
    data_inicio DATE,
    data_fim DATE,
    mandato INTEGER NOT NULL,
    observacoes VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (id_pessoa, id_cargo, data_inicio, mandato)
);

CREATE TABLE IF NOT EXISTS Usuario (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100),
    hashed_password VARCHAR(255) NOT NULL,
    ativo BOOLEAN DEFAULT true,
    role VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Historico (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tipo_operacao TEXT NOT NULL,
    entidade_alvo TEXT NOT NULL,
    operation TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Notificacoes (
    id SERIAL PRIMARY KEY,
    data_solicitacao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    operation TEXT NOT NULL,
    dados_payload JSON NOT NULL,
    tipo_operacao TEXT NOT NULL,
    entidade_alvo TEXT NOT NULL,
    status_aprovacao TEXT NOT NULL DEFAULT 'Pendente',
    data_aprovacao TIMESTAMP,
    regra INTEGER NOT NULL,
    id_afetado INTEGER,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
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
CREATE TRIGGER update_usuario_timestamp
BEFORE UPDATE ON Usuario
FOR EACH ROW
EXECUTE FUNCTION atualizar_timestamp();

-----------------------

CREATE TRIGGER update_historico_timestamp
BEFORE UPDATE ON Historico
FOR EACH ROW
EXECUTE FUNCTION atualizar_timestamp();

-----------------------

CREATE TRIGGER update_notificacoes_timestamp
BEFORE UPDATE ON Notificacoes
FOR EACH ROW
EXECUTE FUNCTION atualizar_timestamp();

