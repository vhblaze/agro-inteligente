"""AgroInteligente - API Flask que integra Sistema Especialista, Logica Fuzzy,
5 algoritmos de Machine Learning e o Agente Inteligente."""
import os
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

import sistema_especialista
import logica_fuzzy
import machine_learning
import agente_inteligente
from data_generator import gerar_dataset

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "talhoes.csv")
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")

app = Flask(__name__)
CORS(app)

# ---- Carrega (ou gera) o dataset e treina os modelos uma unica vez ----
if not os.path.exists(DATA_PATH):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    gerar_dataset().to_csv(DATA_PATH, index=False, encoding="utf-8")

df = pd.read_csv(DATA_PATH)
modelos = machine_learning.ModelosAgro(df)


@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:caminho>")
def arquivos_estaticos(caminho):
    return send_from_directory(FRONTEND_DIR, caminho)


@app.route("/api/dataset-info")
def dataset_info():
    return jsonify({
        "total_registros": len(df),
        "colunas": list(df.columns),
        "amostra": df.head(5).to_dict("records"),
    })


@app.route("/api/analisar", methods=["POST"])
def analisar():
    body = request.get_json(force=True)

    try:
        umidade_solo = float(body["umidade_solo"])
        temperatura = float(body["temperatura"])
        umidade_ar = float(body["umidade_ar"])
        chuva_7dias = float(body["chuva_7dias"])
        chuva_prevista = bool(body.get("chuva_prevista", False))
        historico_pragas = int(body.get("historico_pragas", 0))
        adubacao = float(body.get("adubacao", 150))
        area_ha = float(body.get("area_ha", 10))
    except (KeyError, ValueError, TypeError) as erro:
        return jsonify({"erro": f"Dados de entrada invalidos: {erro}"}), 400

    fatos = {
        "umidade_solo": umidade_solo,
        "temperatura": temperatura,
        "umidade_ar": umidade_ar,
        "chuva_7dias": chuva_7dias,
        "chuva_prevista": chuva_prevista,
        "historico_pragas": historico_pragas,
        "adubacao": adubacao,
        "area_ha": area_ha,
    }

    # 1) Sistema Especialista
    resultado_especialista = sistema_especialista.avaliar(fatos)

    # 2) Logica Fuzzy
    resultado_fuzzy = logica_fuzzy.avaliar(umidade_solo, temperatura)

    # 3) Arvore de Decisao
    resultado_arvore = modelos.prever_arvore(umidade_solo, temperatura, chuva_7dias)

    # 4) KNN
    resultado_knn = modelos.prever_knn(umidade_ar, temperatura, historico_pragas)

    # 5) Regressao Linear (calculada antes do K-Means pois alimenta o cluster)
    resultado_regressao = modelos.prever_regressao(chuva_7dias, adubacao, umidade_solo, area_ha)

    # 6) K-Means
    resultado_kmeans = modelos.classificar_cluster(
        umidade_solo, temperatura, resultado_regressao["produtividade_prevista_ton_ha"]
    )

    # 7) Apriori (padroes gerais do dataset, nao depende da entrada pontual)
    resultado_apriori = modelos.obter_apriori()

    # 8) Agente Inteligente integra tudo
    resultado_agente = agente_inteligente.decidir(
        fatos,
        resultado_especialista,
        resultado_fuzzy,
        resultado_arvore,
        resultado_knn,
        resultado_kmeans,
        resultado_regressao,
    )

    return jsonify({
        "sistema_especialista": resultado_especialista,
        "logica_fuzzy": resultado_fuzzy,
        "arvore_decisao": resultado_arvore,
        "knn": resultado_knn,
        "kmeans": resultado_kmeans,
        "regressao_linear": resultado_regressao,
        "apriori": resultado_apriori,
        "agente_inteligente": resultado_agente,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
