"""API Flask do Sistema de Gestão Penitenciária."""
import os
import sqlite3

from flask import Flask, jsonify, request, send_from_directory

from database import Database
from models import Detento, Agente, Visita, Ocorrencia
from repositories import (DetentoRepository, CelaRepository, AgenteRepository,
                          VisitaRepository, OcorrenciaRepository,
                          EstatisticasRepository)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

db = Database()
db.inicializar()

detentos = DetentoRepository(db)
celas = CelaRepository(db)
agentes = AgenteRepository(db)
visitas = VisitaRepository(db)
ocorrencias = OcorrenciaRepository(db)
estatisticas = EstatisticasRepository(db)


@app.errorhandler(ValueError)
def erro_validacao(e):
    return jsonify({"erro": str(e)}), 400


@app.errorhandler(sqlite3.IntegrityError)
def erro_integridade(e):
    return jsonify({"erro": "Dado duplicado ou inválido: " + str(e)}), 400


# ---------- Front-end ----------
@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


# ---------- Resumo ----------
@app.get("/api/resumo")
def resumo():
    return jsonify(estatisticas.resumo())


# ---------- Detentos ----------
@app.get("/api/detentos")
def listar_detentos():
    return jsonify(detentos.listar())


@app.post("/api/detentos")
def criar_detento():
    dados = request.get_json()
    cela_id = dados.get("cela_id") or None
    if cela_id:
        cela = celas.buscar(int(cela_id))
        if not cela or not cela.tem_vaga():
            raise ValueError("A cela selecionada está lotada.")
    d = Detento(dados["nome"], dados["prontuario"], dados["data_entrada"],
                dados["pena_meses"], "Ativo", cela_id)
    return jsonify(detentos.salvar(d).to_dict()), 201


@app.patch("/api/detentos/<int:id>/status")
def alterar_status(id):
    d = detentos.buscar(id)
    if not d:
        return jsonify({"erro": "Detento não encontrado."}), 404
    novo = request.get_json()["status"]
    if novo not in Detento.STATUS_VALIDOS:
        raise ValueError("Status inválido.")
    d.status = novo
    if novo != "Ativo":
        d.cela_id = None
    return jsonify(detentos.salvar(d).to_dict())


@app.delete("/api/detentos/<int:id>")
def remover_detento(id):
    detentos.remover(id)
    return "", 204


# ---------- Celas ----------
@app.get("/api/celas")
def listar_celas():
    return jsonify(celas.listar())


# ---------- Agentes ----------
@app.get("/api/agentes")
def listar_agentes():
    return jsonify(agentes.listar())


@app.post("/api/agentes")
def criar_agente():
    dados = request.get_json()
    a = Agente(dados["nome"], dados["matricula"], dados["turno"],
               dados.get("bloco_id") or None)
    return jsonify(agentes.salvar(a).to_dict()), 201


# ---------- Visitas ----------
@app.get("/api/visitas")
def listar_visitas():
    return jsonify(visitas.listar())


@app.post("/api/visitas")
def criar_visita():
    dados = request.get_json()
    v = Visita(dados["detento_id"], dados["visitante"], dados["parentesco"],
               dados["data_visita"], dados.get("agente_id") or None)
    return jsonify(visitas.salvar(v).to_dict()), 201


# ---------- Ocorrências ----------
@app.get("/api/ocorrencias")
def listar_ocorrencias():
    return jsonify(ocorrencias.listar())


@app.post("/api/ocorrencias")
def criar_ocorrencia():
    dados = request.get_json()
    o = Ocorrencia(dados["detento_id"], dados["data_ocorrencia"], dados["gravidade"],
                   dados["descricao"], dados.get("agente_id") or None)
    return jsonify(ocorrencias.salvar(o).to_dict()), 201


if __name__ == "__main__":
    app.run(debug=True)
