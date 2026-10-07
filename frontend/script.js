const API_BASE = window.location.origin;

// ---- Navegação simples entre views ----
document.querySelectorAll(".nav-item").forEach(item => {
  item.addEventListener("click", (e) => {
    e.preventDefault();
    document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
    item.classList.add("active");
    const view = item.dataset.view;
    document.querySelectorAll("main > section").forEach(s => s.classList.add("hidden"));
    document.getElementById(`view-${view}`).classList.remove("hidden");
    if (view === "dados") carregarDatasetInfo();
  });
});

async function carregarDatasetInfo() {
  const el = document.getElementById("dataset-info");
  el.textContent = "Carregando...";
  try {
    const resp = await fetch(`${API_BASE}/api/dataset-info`);
    const data = await resp.json();
    let html = `<p><strong>${data.total_registros}</strong> talhões no histórico. Colunas: ${data.colunas.join(", ")}</p>`;
    html += "<table><thead><tr>" + data.colunas.slice(0, 7).map(c => `<th>${c}</th>`).join("") + "</tr></thead><tbody>";
    data.amostra.forEach(linha => {
      html += "<tr>" + data.colunas.slice(0, 7).map(c => `<td>${linha[c]}</td>`).join("") + "</tr>";
    });
    html += "</tbody></table>";
    el.innerHTML = html;
  } catch (err) {
    el.textContent = "Erro ao carregar dataset: " + err.message;
  }
}

// ---- Formulário de análise ----
const form = document.getElementById("form-analise");
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = form.querySelector(".btn-analisar");
  btn.disabled = true;
  btn.textContent = "🔄 Analisando...";

  const payload = {
    umidade_solo: parseFloat(document.getElementById("umidade_solo").value),
    temperatura: parseFloat(document.getElementById("temperatura").value),
    umidade_ar: parseFloat(document.getElementById("umidade_ar").value),
    chuva_7dias: parseFloat(document.getElementById("chuva_7dias").value),
    adubacao: parseFloat(document.getElementById("adubacao").value),
    area_ha: parseFloat(document.getElementById("area_ha").value),
    historico_pragas: parseInt(document.getElementById("historico_pragas").value),
    chuva_prevista: document.getElementById("chuva_prevista").checked,
  };

  try {
    const resp = await fetch(`${API_BASE}/api/analisar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!resp.ok) throw new Error((await resp.json()).erro || "Falha na análise");
    const data = await resp.json();
    renderizarResultados(data);
  } catch (err) {
    alert("Erro: " + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "🔎 Analisar Talhão";
  }
});

function renderizarResultados(data) {
  renderEspecialista(data.sistema_especialista);
  renderFuzzy(data.logica_fuzzy);
  renderArvore(data.arvore_decisao);
  renderKnn(data.knn);
  renderKmeans(data.kmeans);
  renderRegressao(data.regressao_linear);
  renderApriori(data.apriori);
  renderAgente(data.agente_inteligente);
}

function setCard(id, html) {
  const el = document.getElementById(id);
  el.classList.remove("placeholder");
  el.innerHTML = html;
}

function renderEspecialista(r) {
  const regras = r.regras_ativadas.map(x => `<li>${x}</li>`).join("");
  setCard("out-especialista", `
    <p><strong>Decisão final:</strong> <span class="tag">${r.decisao_final}</span></p>
    <p><strong>Regras ativadas:</strong></p>
    <ul>${regras}</ul>
    <p><em>${r.mecanismo_inferencia}</em></p>
  `);
}

function renderFuzzy(r) {
  const pu = r.pertinencia_umidade, pt = r.pertinencia_temperatura;
  setCard("out-fuzzy", `
    <div class="metric-row"><span>Necessidade de irrigação</span><strong>${r.necessidade_irrigacao_rotulo} (${r.necessidade_irrigacao_percentual}%)</strong></div>
    <p><strong>Pertinência umidade:</strong> seca ${pu.baixa}, ideal ${pu.media}, encharcada ${pu.alta}</p>
    <p><strong>Pertinência temperatura:</strong> fria ${pt.fria}, amena ${pt.amena}, quente ${pt.quente}</p>
    <p><strong>${r.regras_ativadas.length}</strong> regras fuzzy ativadas nesta inferência.</p>
  `);
}

function renderArvore(r) {
  const probs = Object.entries(r.probabilidades).map(([k, v]) => `<span class="tag">${k}: ${(v*100).toFixed(0)}%</span>`).join(" ");
  setCard("out-arvore", `
    <p><strong>Classificação:</strong> <span class="tag">${r.classificacao}</span></p>
    <p>${probs}</p>
    <pre>${r.regras_arvore}</pre>
  `);
}

function renderKnn(r) {
  const linhas = r.vizinhos_mais_proximos.map((v, i) =>
    `<tr><td>${i+1}</td><td>${v.umidade_ar}</td><td>${v.temperatura}</td><td>${v.historico_pragas}</td><td>${v.risco_praga}</td></tr>`
  ).join("");
  setCard("out-knn", `
    <p><strong>Risco de praga previsto:</strong> <span class="tag">${r.classificacao_risco_praga}</span></p>
    <table><thead><tr><th>#</th><th>Umid. ar</th><th>Temp.</th><th>Hist. pragas</th><th>Risco</th></tr></thead>
    <tbody>${linhas}</tbody></table>
  `);
}

function renderKmeans(r) {
  const dist = Object.entries(r.distribuicao_talhoes).map(([g, n]) => `<span class="tag">${g} (${r.nomes_grupos[g]}): ${n}</span>`).join(" ");
  setCard("out-kmeans", `
    <p><strong>Grupo do talhão:</strong> <span class="tag">Grupo ${r.cluster} — ${r.perfil}</span></p>
    <p><strong>Distribuição no histórico:</strong></p>
    <p>${dist}</p>
  `);
}

function renderRegressao(r) {
  const coefs = Object.entries(r.coeficientes).map(([k, v]) => `<li>${k}: ${v}</li>`).join("");
  setCard("out-regressao", `
    <div class="metric-row"><span>Produtividade prevista</span><strong>${r.produtividade_prevista_ton_ha} ton/ha</strong></div>
    <p><strong>R² do modelo:</strong> ${r.r2_treino}</p>
    <p><strong>Coeficientes:</strong></p>
    <ul>${coefs}</ul>
  `);
}

function renderApriori(r) {
  const itens = r.itens_frequentes.map(i => `<li>{${i.itens.join(", ")}} — suporte ${i.suporte}</li>`).join("");
  const regras = r.regras_associacao.map(rr =>
    `<li>SE {${rr.se.join(", ")}} ENTÃO {${rr.entao.join(", ")}} — confiança ${(rr.confianca*100).toFixed(0)}%, lift ${rr.lift}</li>`
  ).join("") || "<li>Nenhuma regra forte encontrada com os limiares atuais.</li>";
  setCard("out-apriori", `
    <p><strong>Itens frequentes (histórico de talhões):</strong></p>
    <ul>${itens}</ul>
    <p><strong>Regras de associação relacionadas a pragas:</strong></p>
    <ul>${regras}</ul>
  `);
}

function renderAgente(r) {
  const acoes = r.acoes_recomendadas.map(a => `<li>${a}</li>`).join("");
  const motivos = r.justificativas.map(m => `<li>${m}</li>`).join("");
  setCard("out-agente", `
    <div class="agente-resumo">${r.resumo_decisao}</div>
    <p><strong>Ações recomendadas:</strong></p>
    <ul>${acoes}</ul>
    <p><strong>Justificativas (integração das técnicas):</strong></p>
    <ul>${motivos}</ul>
  `);
}
