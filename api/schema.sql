CREATE TABLE IF NOT EXISTS Pessoa (
    id_pessoa INTEGER PRIMARY KEY AUTOINCREMENT, 
    nome TEXT NOT NULL,
    ativo INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Orgao (
    id_orgao INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    ativo INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Cargo (
    id_cargo INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    ativo INTEGER NOT NULL,
    id_orgao INTEGER REFERENCES Orgao (id_orgao),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Portaria (
    id_portaria INTEGER PRIMARY KEY AUTOINCREMENT,
    numero INTEGER NOT NULL,
    data_portaria TEXT NOT NULL,
    observacoes TEXT,
    ativo INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Ocupacao (
    id_ocupacao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_pessoa INTEGER REFERENCES Pessoa (id_pessoa) NOT NULL,
    id_cargo INTEGER REFERENCES Cargo (id_cargo) NOT NULL,
    id_portaria INTEGER REFERENCES Portaria (id_portaria),
    data_inicio TEXT,
    data_fim TEXT,
    mandato INTEGER NOT NULL,
    observacoes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER update_portaria_timestamp
AFTER UPDATE ON Portaria
FOR EACH ROW
BEGIN
    UPDATE Portaria
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id_portaria = OLD.id_portaria;
END;

CREATE TRIGGER update_pessoa_timestamp
AFTER UPDATE ON Pessoa
FOR EACH ROW
BEGIN
    UPDATE Pessoa
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id_pessoa = OLD.id_pessoa;
END;

CREATE TRIGGER update_orgao_timestamp
AFTER UPDATE ON Orgao
FOR EACH ROW
BEGIN
    UPDATE Orgao
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id_orgao = OLD.id_orgao;
END;

CREATE TRIGGER update_cargo_timestamp
AFTER UPDATE ON Cargo
FOR EACH ROW
BEGIN
    UPDATE Cargo
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id_cargo = OLD.id_cargo;
END;

CREATE TRIGGER update_ocupacao_timestamp
AFTER UPDATE ON Ocupacao
FOR EACH ROW
BEGIN
    UPDATE Ocupacao
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id_ocupacao = OLD.id_ocupacao;
END;
