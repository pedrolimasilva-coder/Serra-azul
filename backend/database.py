"""Camada de acesso ao banco de dados (SQLite)."""
import os
import sqlite3
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "penitenciaria.db")


class Database:
    """Gerencia conexões e a criação inicial do banco."""

    def __init__(self, caminho=DB_PATH):
        self._caminho = caminho

    @contextmanager
    def conexao(self):
        conn = sqlite3.connect(self._caminho)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _executar_script(self, nome_arquivo):
        with open(os.path.join(DB_DIR, nome_arquivo), encoding="utf-8") as f:
            script = f.read()
        with self.conexao() as conn:
            conn.executescript(script)

    def inicializar(self):
        """Cria as tabelas e insere dados de exemplo se o banco ainda não existir."""
        novo = not os.path.exists(self._caminho)
        self._executar_script("schema.sql")
        if novo:
            self._executar_script("seed.sql")
