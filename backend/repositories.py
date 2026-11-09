"""Repositórios: fazem a ponte entre os objetos (POO) e o banco (SQL)."""
from models import Detento, Agente, Cela, Visita, Ocorrencia


class Repositorio:
    """Classe base com operações comuns."""
    tabela = None

    def __init__(self, db):
        self.db = db

    def remover(self, id):
        with self.db.conexao() as conn:
            conn.execute(f"DELETE FROM {self.tabela} WHERE id = ?", (id,))


class DetentoRepository(Repositorio):
    tabela = "detento"

    def _para_objeto(self, row):
        return Detento(row["nome"], row["prontuario"], row["data_entrada"],
                       row["pena_meses"], row["status"], row["cela_id"], row["id"])

    def listar(self):
        with self.db.conexao() as conn:
            rows = conn.execute("""
                SELECT d.*, c.numero AS cela, b.nome AS bloco
                FROM detento d
                LEFT JOIN cela c ON c.id = d.cela_id
                LEFT JOIN bloco b ON b.id = c.bloco_id
                ORDER BY d.nome""").fetchall()
        resultado = []
        for r in rows:
            dados = self._para_objeto(r).to_dict()
            dados["cela"] = f"{r['bloco']} - {r['cela']}" if r["cela"] else "Sem cela"
            resultado.append(dados)
        return resultado

    def buscar(self, id):
        with self.db.conexao() as conn:
            row = conn.execute("SELECT * FROM detento WHERE id = ?", (id,)).fetchone()
        return self._para_objeto(row) if row else None

    def salvar(self, d: Detento):
        with self.db.conexao() as conn:
            if d.id:
                conn.execute("""UPDATE detento SET nome=?, prontuario=?, data_entrada=?,
                                pena_meses=?, status=?, cela_id=? WHERE id=?""",
                             (d.nome, d.prontuario, d.data_entrada.isoformat(),
                              d.pena_meses, d.status, d.cela_id, d.id))
            else:
                cur = conn.execute("""INSERT INTO detento
                                (nome, prontuario, data_entrada, pena_meses, status, cela_id)
                                VALUES (?, ?, ?, ?, ?, ?)""",
                                   (d.nome, d.prontuario, d.data_entrada.isoformat(),
                                    d.pena_meses, d.status, d.cela_id))
                d.id = cur.lastrowid
        return d


class CelaRepository(Repositorio):
    tabela = "cela"

    def listar(self):
        with self.db.conexao() as conn:
            rows = conn.execute("""SELECT v.*, c.bloco_id FROM vw_ocupacao_celas v
                                   JOIN cela c ON c.id = v.id
                                   ORDER BY v.bloco, v.numero""").fetchall()
        lista = []
        for r in rows:
            dados = Cela(r["numero"], r["capacidade"], r["bloco_id"],
                         r["ocupantes"], r["id"]).to_dict()
            dados["bloco"] = r["bloco"]
            lista.append(dados)
        return lista

    def buscar(self, id):
        with self.db.conexao() as conn:
            r = conn.execute("""SELECT v.*, c.bloco_id FROM vw_ocupacao_celas v
                                JOIN cela c ON c.id = v.id WHERE v.id = ?""",
                             (id,)).fetchone()
        return Cela(r["numero"], r["capacidade"], r["bloco_id"],
                    r["ocupantes"], r["id"]) if r else None


class AgenteRepository(Repositorio):
    tabela = "agente"

    def listar(self):
        with self.db.conexao() as conn:
            rows = conn.execute("""SELECT a.*, b.nome AS bloco FROM agente a
                                   LEFT JOIN bloco b ON b.id = a.bloco_id
                                   ORDER BY a.nome""").fetchall()
        lista = []
        for r in rows:
            dados = Agente(r["nome"], r["matricula"], r["turno"],
                           r["bloco_id"], r["id"]).to_dict()
            dados["bloco"] = r["bloco"] or "-"
            lista.append(dados)
        return lista

    def salvar(self, a: Agente):
        with self.db.conexao() as conn:
            cur = conn.execute("""INSERT INTO agente (nome, matricula, turno, bloco_id)
                                  VALUES (?, ?, ?, ?)""",
                               (a.nome, a.matricula, a.turno, a.bloco_id))
            a.id = cur.lastrowid
        return a


class VisitaRepository(Repositorio):
    tabela = "visita"

    def listar(self):
        with self.db.conexao() as conn:
            rows = conn.execute("""SELECT v.*, d.nome AS detento FROM visita v
                                   JOIN detento d ON d.id = v.detento_id
                                   ORDER BY v.data_visita DESC""").fetchall()
        return [dict(r) for r in rows]

    def salvar(self, v: Visita):
        with self.db.conexao() as conn:
            cur = conn.execute("""INSERT INTO visita
                                  (detento_id, visitante, parentesco, data_visita, agente_id)
                                  VALUES (?, ?, ?, ?, ?)""",
                               (v.detento_id, v.visitante, v.parentesco,
                                v.data_visita, v.agente_id))
            v.id = cur.lastrowid
        return v


class OcorrenciaRepository(Repositorio):
    tabela = "ocorrencia"

    def listar(self):
        with self.db.conexao() as conn:
            rows = conn.execute("""SELECT o.*, d.nome AS detento, a.nome AS agente
                                   FROM ocorrencia o
                                   JOIN detento d ON d.id = o.detento_id
                                   LEFT JOIN agente a ON a.id = o.agente_id
                                   ORDER BY o.data_ocorrencia DESC""").fetchall()
        return [dict(r) for r in rows]

    def salvar(self, o: Ocorrencia):
        with self.db.conexao() as conn:
            cur = conn.execute("""INSERT INTO ocorrencia
                        (detento_id, agente_id, data_ocorrencia, gravidade, descricao)
                        VALUES (?, ?, ?, ?, ?)""",
                               (o.detento_id, o.agente_id, o.data_ocorrencia,
                                o.gravidade, o.descricao))
            o.id = cur.lastrowid
        return o


class EstatisticasRepository(Repositorio):
    def resumo(self):
        with self.db.conexao() as conn:
            def um(sql):
                return conn.execute(sql).fetchone()[0]
            return {
                "detentos_ativos": um("SELECT COUNT(*) FROM detento WHERE status='Ativo'"),
                "capacidade_total": um("SELECT COALESCE(SUM(capacidade),0) FROM cela"),
                "agentes": um("SELECT COUNT(*) FROM agente"),
                "visitas": um("SELECT COUNT(*) FROM visita"),
                "ocorrencias_graves": um(
                    "SELECT COUNT(*) FROM ocorrencia WHERE gravidade='Grave'"),
            }
