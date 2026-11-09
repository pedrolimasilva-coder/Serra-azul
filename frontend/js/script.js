// Front-end: consome a API Flask e atualiza as telas

const api = {
  async get(url) {
    const r = await fetch(url);
    return r.json();
  },
  async enviar(url, metodo, dados) {
    const r = await fetch(url, {
      method: metodo,
      headers: { "Content-Type": "application/json" },
      body: dados ? JSON.stringify(dados) : undefined,
    });
    if (!r.ok) {
      const erro = await r.json().catch(() => ({}));
      throw new Error(erro.erro || "Erro na requisição");
    }
    return r.status === 204 ? null : r.json();
  },
};

function avisar(msg, erro = false) {
  const el = document.getElementById("aviso");
  el.textContent = msg;
  el.className = "aviso visivel" + (erro ? " erro" : "");
  setTimeout(() => (el.className = "aviso"), 2800);
}

const formatarData = (iso) => iso ? iso.split("-").reverse().join("/") : "-";
const escapar = (txt) => String(txt ?? "").replace(/[&<>"']/g,
  (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

// ---------- Abas ----------
document.querySelectorAll(".aba").forEach((botao) => {
  botao.addEventListener("click", () => {
    document.querySelectorAll(".aba, .secao").forEach((el) => el.classList.remove("ativa"));
    botao.classList.add("ativa");
    document.getElementById(botao.dataset.aba).classList.add("ativa");
    carregar[botao.dataset.aba]();
  });
});

// ---------- Carregamento de cada tela ----------
let listaDetentos = [];

const carregar = {
  async painel() {
    const r = await api.get("/api/resumo");
    const itens = [
      [r.detentos_ativos, "Detentos ativos"],
      [`${r.detentos_ativos}/${r.capacidade_total}`, "Ocupação total"],
      [r.agentes, "Agentes"],
      [r.visitas, "Visitas registradas"],
      [r.ocorrencias_graves, "Ocorrências graves"],
    ];
    document.getElementById("cards-resumo").innerHTML = itens
      .map(([v, t]) => `<div class="card"><strong>${v}</strong><span>${t}</span></div>`)
      .join("");
  },

  async detentos() {
    listaDetentos = await api.get("/api/detentos");
    renderizarDetentos(listaDetentos);
    const celas = await api.get("/api/celas");
    document.getElementById("select-cela").innerHTML =
      '<option value="">Sem cela</option>' +
      celas.map((c) => `<option value="${c.id}" ${c.tem_vaga ? "" : "disabled"}>
        ${c.bloco} - ${c.numero} (${c.ocupantes}/${c.capacidade})</option>`).join("");
  },

  async celas() {
    const celas = await api.get("/api/celas");
    document.getElementById("grade-celas").innerHTML = celas.map((c) => `
      <div class="cela ${c.tem_vaga ? "" : "lotada"}">
        <h3>${c.numero}</h3>
        <small>${c.bloco} · ${c.ocupantes}/${c.capacidade}</small>
        <div class="vagas">${Array.from({ length: c.capacidade },
          (_, i) => `<i class="${i < c.ocupantes ? "ocupada" : ""}"></i>`).join("")}</div>
      </div>`).join("");
  },

  async agentes() {
    const lista = await api.get("/api/agentes");
    document.getElementById("tabela-agentes").innerHTML = lista.map((a) => `
      <tr><td class="mono">${escapar(a.matricula)}</td><td>${escapar(a.nome)}</td>
      <td>${a.turno}</td><td>${escapar(a.bloco)}</td></tr>`).join("");
  },

  async visitas() {
    await preencherSelectDetentos();
    const lista = await api.get("/api/visitas");
    document.getElementById("tabela-visitas").innerHTML = lista.map((v) => `
      <tr><td>${formatarData(v.data_visita)}</td><td>${escapar(v.detento)}</td>
      <td>${escapar(v.visitante)}</td><td>${escapar(v.parentesco)}</td></tr>`).join("");
  },

  async ocorrencias() {
    await preencherSelectDetentos();
    const lista = await api.get("/api/ocorrencias");
    document.getElementById("tabela-ocorrencias").innerHTML = lista.map((o) => `
      <tr><td>${formatarData(o.data_ocorrencia)}</td><td>${escapar(o.detento)}</td>
      <td><span class="tag ${o.gravidade}">${o.gravidade}</span></td>
      <td>${escapar(o.descricao)}</td><td>${escapar(o.agente || "-")}</td></tr>`).join("");
  },
};

function renderizarDetentos(lista) {
  document.getElementById("tabela-detentos").innerHTML = lista.map((d) => `
    <tr>
      <td class="mono">${escapar(d.prontuario)}</td>
      <td>${escapar(d.nome)}</td>
      <td>${escapar(d.cela)}</td>
      <td><span class="barra"><i style="width:${d.percentual_cumprido}%"></i></span>
          ${d.percentual_cumprido}%</td>
      <td>${formatarData(d.previsao_saida)}</td>
      <td class="acoes">
        <select data-id="${d.id}" class="mudar-status">
          ${["Ativo", "Transferido", "Liberado"].map((s) =>
            `<option ${s === d.status ? "selected" : ""}>${s}</option>`).join("")}
        </select>
      </td>
      <td><button class="btn-remover" data-id="${d.id}" title="Remover">✕</button></td>
    </tr>`).join("");
}

async function preencherSelectDetentos() {
  const lista = await api.get("/api/detentos");
  document.querySelectorAll(".select-detento").forEach((sel) => {
    sel.innerHTML = '<option value="">Selecione o detento</option>' +
      lista.filter((d) => d.status === "Ativo")
        .map((d) => `<option value="${d.id}">${escapar(d.nome)} (${escapar(d.prontuario)})</option>`)
        .join("");
  });
}

// ---------- Busca ----------
document.getElementById("busca-detento").addEventListener("input", (e) => {
  const termo = e.target.value.toLowerCase();
  renderizarDetentos(listaDetentos.filter((d) =>
    d.nome.toLowerCase().includes(termo) || d.prontuario.toLowerCase().includes(termo)));
});

// ---------- Ações da tabela de detentos ----------
document.getElementById("tabela-detentos").addEventListener("change", async (e) => {
  if (!e.target.classList.contains("mudar-status")) return;
  try {
    await api.enviar(`/api/detentos/${e.target.dataset.id}/status`, "PATCH",
      { status: e.target.value });
    avisar("Status atualizado.");
    carregar.detentos();
  } catch (err) { avisar(err.message, true); }
});

document.getElementById("tabela-detentos").addEventListener("click", async (e) => {
  if (!e.target.classList.contains("btn-remover")) return;
  if (!confirm("Remover este detento e seus registros?")) return;
  await api.enviar(`/api/detentos/${e.target.dataset.id}`, "DELETE");
  avisar("Detento removido.");
  carregar.detentos();
});

// ---------- Formulários ----------
function ligarFormulario(id, url, aoSalvar, mensagem) {
  document.getElementById(id).addEventListener("submit", async (e) => {
    e.preventDefault();
    const dados = Object.fromEntries(new FormData(e.target));
    try {
      await api.enviar(url, "POST", dados);
      e.target.reset();
      avisar(mensagem);
      aoSalvar();
    } catch (err) { avisar(err.message, true); }
  });
}

ligarFormulario("form-detento", "/api/detentos", carregar.detentos, "Detento cadastrado.");
ligarFormulario("form-agente", "/api/agentes", carregar.agentes, "Agente cadastrado.");
ligarFormulario("form-visita", "/api/visitas", carregar.visitas, "Visita registrada.");
ligarFormulario("form-ocorrencia", "/api/ocorrencias", carregar.ocorrencias, "Ocorrência registrada.");

carregar.painel();
