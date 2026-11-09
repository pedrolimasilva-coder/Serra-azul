"""Modelos do domínio (Programação Orientada a Objetos)."""
from abc import ABC, abstractmethod
from datetime import date


class Pessoa(ABC):
    """Classe abstrata base para pessoas do sistema."""

    def __init__(self, nome, id=None):
        self.id = id
        self.nome = nome

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, valor):
        if not valor or len(valor.strip()) < 3:
            raise ValueError("Nome deve ter pelo menos 3 caracteres.")
        self._nome = valor.strip()

    @abstractmethod
    def identificacao(self):
        """Cada tipo de pessoa tem seu próprio identificador."""

    def __str__(self):
        return f"{self.nome} ({self.identificacao()})"


class Detento(Pessoa):
    STATUS_VALIDOS = ("Ativo", "Transferido", "Liberado")

    def __init__(self, nome, prontuario, data_entrada, pena_meses,
                 status="Ativo", cela_id=None, id=None):
        super().__init__(nome, id)
        self.prontuario = prontuario
        self.data_entrada = data_entrada if isinstance(data_entrada, date) \
            else date.fromisoformat(str(data_entrada))
        self.pena_meses = int(pena_meses)
        if self.pena_meses <= 0:
            raise ValueError("Pena deve ser maior que zero.")
        if status not in self.STATUS_VALIDOS:
            raise ValueError("Status inválido.")
        self.status = status
        self.cela_id = cela_id

    def identificacao(self):
        return self.prontuario

    def previsao_saida(self):
        """Data prevista de término da pena."""
        total = self.data_entrada.month - 1 + self.pena_meses
        ano = self.data_entrada.year + total // 12
        mes = total % 12 + 1
        dia = min(self.data_entrada.day, 28)
        return date(ano, mes, dia)

    def percentual_cumprido(self, hoje=None):
        hoje = hoje or date.today()
        dias_total = (self.previsao_saida() - self.data_entrada).days
        dias_cumpridos = (hoje - self.data_entrada).days
        return max(0, min(100, round(dias_cumpridos / dias_total * 100)))

    def to_dict(self):
        return {
            "id": self.id, "nome": self.nome, "prontuario": self.prontuario,
            "data_entrada": self.data_entrada.isoformat(),
            "pena_meses": self.pena_meses, "status": self.status,
            "cela_id": self.cela_id,
            "previsao_saida": self.previsao_saida().isoformat(),
            "percentual_cumprido": self.percentual_cumprido(),
        }


class Agente(Pessoa):
    TURNOS = ("Manhã", "Tarde", "Noite")

    def __init__(self, nome, matricula, turno, bloco_id=None, id=None):
        super().__init__(nome, id)
        if turno not in self.TURNOS:
            raise ValueError("Turno inválido.")
        self.matricula = matricula
        self.turno = turno
        self.bloco_id = bloco_id

    def identificacao(self):
        return self.matricula

    def to_dict(self):
        return {"id": self.id, "nome": self.nome, "matricula": self.matricula,
                "turno": self.turno, "bloco_id": self.bloco_id}


class Cela:
    def __init__(self, numero, capacidade, bloco_id, ocupantes=0, id=None):
        self.id = id
        self.numero = numero
        self.capacidade = int(capacidade)
        self.bloco_id = bloco_id
        self.ocupantes = ocupantes

    def tem_vaga(self):
        return self.ocupantes < self.capacidade

    def to_dict(self):
        return {"id": self.id, "numero": self.numero, "capacidade": self.capacidade,
                "bloco_id": self.bloco_id, "ocupantes": self.ocupantes,
                "tem_vaga": self.tem_vaga()}


class Visita:
    def __init__(self, detento_id, visitante, parentesco, data_visita,
                 agente_id=None, id=None):
        self.id = id
        self.detento_id = detento_id
        self.visitante = visitante
        self.parentesco = parentesco
        self.data_visita = data_visita
        self.agente_id = agente_id

    def to_dict(self):
        return vars(self)


class Ocorrencia:
    GRAVIDADES = ("Leve", "Média", "Grave")

    def __init__(self, detento_id, data_ocorrencia, gravidade, descricao,
                 agente_id=None, id=None):
        if gravidade not in self.GRAVIDADES:
            raise ValueError("Gravidade inválida.")
        self.id = id
        self.detento_id = detento_id
        self.agente_id = agente_id
        self.data_ocorrencia = data_ocorrencia
        self.gravidade = gravidade
        self.descricao = descricao

    def to_dict(self):
        return vars(self)
