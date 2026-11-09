-- Dados fictícios de exemplo

INSERT INTO bloco (nome, nivel_seguranca) VALUES
    ('Bloco A', 'Mínima'),
    ('Bloco B', 'Média'),
    ('Bloco C', 'Máxima');

INSERT INTO cela (numero, capacidade, bloco_id) VALUES
    ('101', 4, 1), ('102', 4, 1),
    ('201', 2, 2), ('202', 2, 2),
    ('301', 1, 3), ('302', 1, 3);

INSERT INTO agente (nome, matricula, turno, bloco_id) VALUES
    ('Marta Siqueira',  'AG-1001', 'Manhã', 1),
    ('Rogério Paiva',   'AG-1002', 'Tarde', 2),
    ('Helena Brandão',  'AG-1003', 'Noite', 3);

INSERT INTO detento (nome, prontuario, data_entrada, pena_meses, status, cela_id) VALUES
    ('Caio Mendonça',   'PR-0001', '2024-03-12', 48, 'Ativo', 1),
    ('Diego Torres',    'PR-0002', '2025-01-20', 24, 'Ativo', 1),
    ('Fábio Lacerda',   'PR-0003', '2023-08-05', 96, 'Ativo', 3),
    ('Gustavo Ramos',   'PR-0004', '2022-11-30', 180, 'Ativo', 5),
    ('Igor Nogueira',   'PR-0005', '2025-06-14', 12, 'Ativo', 2);

INSERT INTO visita (detento_id, visitante, parentesco, data_visita, agente_id) VALUES
    (1, 'Luciana Mendonça', 'Mãe',    '2026-10-04', 1),
    (3, 'Paula Lacerda',    'Esposa', '2026-10-11', 2);

INSERT INTO ocorrencia (detento_id, agente_id, data_ocorrencia, gravidade, descricao) VALUES
    (4, 3, '2026-09-22', 'Grave', 'Objeto não autorizado encontrado na revista da cela.'),
    (2, 1, '2026-10-02', 'Leve',  'Atraso na contagem matinal.');
