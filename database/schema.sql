-- Sistema de Gestão Penitenciária - Penitenciária Estadual Serra Azul (fictícia)
-- Banco de dados: SQLite

CREATE TABLE IF NOT EXISTS bloco (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT    NOT NULL UNIQUE,
    nivel_seguranca TEXT NOT NULL CHECK (nivel_seguranca IN ('Mínima', 'Média', 'Máxima'))
);

CREATE TABLE IF NOT EXISTS cela (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    numero      TEXT    NOT NULL,
    capacidade  INTEGER NOT NULL CHECK (capacidade > 0),
    bloco_id    INTEGER NOT NULL REFERENCES bloco(id) ON DELETE RESTRICT,
    UNIQUE (numero, bloco_id)
);

CREATE TABLE IF NOT EXISTS agente (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT    NOT NULL,
    matricula   TEXT    NOT NULL UNIQUE,
    turno       TEXT    NOT NULL CHECK (turno IN ('Manhã', 'Tarde', 'Noite')),
    bloco_id    INTEGER REFERENCES bloco(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS detento (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nome            TEXT    NOT NULL,
    prontuario      TEXT    NOT NULL UNIQUE,
    data_entrada    DATE    NOT NULL,
    pena_meses      INTEGER NOT NULL CHECK (pena_meses > 0),
    status          TEXT    NOT NULL DEFAULT 'Ativo'
                    CHECK (status IN ('Ativo', 'Transferido', 'Liberado')),
    cela_id         INTEGER REFERENCES cela(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS visita (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    detento_id      INTEGER NOT NULL REFERENCES detento(id) ON DELETE CASCADE,
    visitante       TEXT    NOT NULL,
    parentesco      TEXT    NOT NULL,
    data_visita     DATE    NOT NULL,
    agente_id       INTEGER REFERENCES agente(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS ocorrencia (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    detento_id      INTEGER NOT NULL REFERENCES detento(id) ON DELETE CASCADE,
    agente_id       INTEGER REFERENCES agente(id) ON DELETE SET NULL,
    data_ocorrencia DATE    NOT NULL,
    gravidade       TEXT    NOT NULL CHECK (gravidade IN ('Leve', 'Média', 'Grave')),
    descricao       TEXT    NOT NULL
);

-- Visão: ocupação de cada cela
CREATE VIEW IF NOT EXISTS vw_ocupacao_celas AS
SELECT c.id,
       c.numero,
       b.nome AS bloco,
       c.capacidade,
       COUNT(d.id) AS ocupantes
FROM cela c
JOIN bloco b ON b.id = c.bloco_id
LEFT JOIN detento d ON d.cela_id = c.id AND d.status = 'Ativo'
GROUP BY c.id;
