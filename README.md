# Sistema de Gestão Penitenciária — Serra Azul

Projeto Integrado (DWS, POO e BD). Sistema web para administrar uma penitenciária fictícia: detentos, celas, agentes, visitas e ocorrências disciplinares.

## Tecnologias

| Camada     | Tecnologia                          |
|------------|-------------------------------------|
| Banco      | SQLite (scripts em `database/`)     |
| Back-end   | Python 3, Flask, POO                |
| Front-end  | HTML, CSS e JavaScript (fetch API)  |

## Estrutura

```
penitenciaria/
├── backend/
│   ├── app.py            # Rotas da API (Flask)
│   ├── database.py       # Conexão e criação do banco
│   ├── models.py         # Classes do domínio (POO)
│   └── repositories.py   # Acesso a dados (SQL)
├── database/
│   ├── schema.sql        # Tabelas, restrições e view
│   └── seed.sql          # Dados de exemplo
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/script.js
└── requirements.txt
```

## Como executar

```bash
python -m venv venv
# Windows: venv\Scripts\activate   |   Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
cd backend
python app.py
```

Acesse **http://127.0.0.1:5000**. O banco `database/penitenciaria.db` é criado automaticamente na primeira execução, já com dados de exemplo. Para recomeçar do zero, apague esse arquivo.

## Conceitos de POO aplicados

- **Abstração:** `Pessoa` é uma classe abstrata (`ABC`) com o método abstrato `identificacao()`.
- **Herança:** `Detento` e `Agente` herdam de `Pessoa`; os repositórios herdam de `Repositorio`.
- **Polimorfismo:** cada subclasse implementa `identificacao()` do seu jeito (prontuário x matrícula).
- **Encapsulamento:** o nome é validado por `@property`/setter; regras como `tem_vaga()`, `previsao_saida()` e `percentual_cumprido()` ficam dentro das classes.

## Banco de dados

- 6 tabelas relacionadas: `bloco`, `cela`, `agente`, `detento`, `visita`, `ocorrencia`
- Chaves estrangeiras com `ON DELETE` (RESTRICT, SET NULL, CASCADE)
- Restrições `CHECK` e `UNIQUE`
- View `vw_ocupacao_celas` com `JOIN`, `LEFT JOIN` e `GROUP BY`

## API

| Método | Rota                              | Descrição                    |
|--------|-----------------------------------|------------------------------|
| GET    | `/api/resumo`                     | Números do painel            |
| GET    | `/api/detentos`                   | Lista detentos               |
| POST   | `/api/detentos`                   | Cadastra (valida vaga na cela) |
| PATCH  | `/api/detentos/<id>/status`       | Altera status                |
| DELETE | `/api/detentos/<id>`              | Remove detento               |
| GET    | `/api/celas`                      | Celas e ocupação             |
| GET/POST | `/api/agentes`                  | Lista / cadastra agentes     |
| GET/POST | `/api/visitas`                  | Lista / registra visitas     |
| GET/POST | `/api/ocorrencias`              | Lista / registra ocorrências |

## Integrantes

- Nome — RA
- Nome — RA
