"""Treina e aplica os 5 algoritmos de Machine Learning exigidos no projeto:
Arvore de Decisao, KNN, K-Means, Regressao Linear e Apriori.
"""
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder


class ModelosAgro:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self._treinar_arvore()
        self._treinar_knn()
        self._treinar_kmeans()
        self._treinar_regressao()
        self._treinar_apriori()

    # 1) ARVORE DE DECISAO -> classifica necessidade de irrigacao
    def _treinar_arvore(self):
        X = self.df[["umidade_solo", "temperatura", "chuva_7dias"]]
        y = self.df["necessidade_irrigacao"]
        self.arvore = DecisionTreeClassifier(max_depth=4, random_state=42)
        self.arvore.fit(X, y)
        self.arvore_regras_texto = export_text(
            self.arvore, feature_names=["umidade_solo", "temperatura", "chuva_7dias"]
        )

    def prever_arvore(self, umidade_solo, temperatura, chuva_7dias):
        X = pd.DataFrame([[umidade_solo, temperatura, chuva_7dias]], columns=["umidade_solo", "temperatura", "chuva_7dias"])
        pred = self.arvore.predict(X)[0]
        proba = dict(zip(self.arvore.classes_, self.arvore.predict_proba(X)[0].round(3)))
        return {
            "classificacao": pred,
            "probabilidades": proba,
            "regras_arvore": self.arvore_regras_texto,
        }

    # 2) KNN -> classifica risco de praga comparando com talhoes semelhantes
    def _treinar_knn(self):
        self.knn_features = ["umidade_ar", "temperatura", "historico_pragas"]
        X = self.df[self.knn_features]
        y = self.df["risco_praga"]
        self.knn_scaler = StandardScaler().fit(X)
        Xs = self.knn_scaler.transform(X)
        self.knn = KNeighborsClassifier(n_neighbors=5)
        self.knn.fit(Xs, y)

    def prever_knn(self, umidade_ar, temperatura, historico_pragas):
        X = pd.DataFrame([[umidade_ar, temperatura, historico_pragas]], columns=self.knn_features)
        Xs = self.knn_scaler.transform(X)
        pred = self.knn.predict(Xs)[0]
        dist, idx = self.knn.kneighbors(Xs, n_neighbors=5)
        vizinhos = self.df.iloc[idx[0]][self.knn_features + ["risco_praga"]].to_dict("records")
        return {
            "classificacao_risco_praga": pred,
            "vizinhos_mais_proximos": vizinhos,
            "distancias": dist[0].round(3).tolist(),
        }

    # 3) K-MEANS -> agrupa talhoes em perfis
    def _treinar_kmeans(self):
        self.kmeans_features = ["umidade_solo", "temperatura", "produtividade"]
        X = self.df[self.kmeans_features]
        self.kmeans_scaler = StandardScaler().fit(X)
        Xs = self.kmeans_scaler.transform(X)
        self.kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        self.df["cluster"] = self.kmeans.fit_predict(Xs)

        medias = self.df.groupby("cluster")[self.kmeans_features].mean()
        self.cluster_nomes = {}
        for cluster_id, row in medias.iterrows():
            if row["produtividade"] == medias["produtividade"].max():
                nome = "Alta produtividade"
            elif row["umidade_solo"] == medias["umidade_solo"].min():
                nome = "Estresse hidrico"
            else:
                nome = "Perfil intermediario"
            self.cluster_nomes[cluster_id] = nome

    def classificar_cluster(self, umidade_solo, temperatura, produtividade_estimada):
        X = pd.DataFrame([[umidade_solo, temperatura, produtividade_estimada]], columns=self.kmeans_features)
        Xs = self.kmeans_scaler.transform(X)
        cluster_id = int(self.kmeans.predict(Xs)[0])
        distribuicao = self.df["cluster"].value_counts().sort_index().to_dict()
        return {
            "cluster": cluster_id,
            "perfil": self.cluster_nomes.get(cluster_id, "Perfil"),
            "distribuicao_talhoes": {f"Grupo {k}": int(v) for k, v in distribuicao.items()},
            "nomes_grupos": {f"Grupo {k}": v for k, v in self.cluster_nomes.items()},
        }

    # 4) REGRESSAO LINEAR -> preve produtividade (ton/ha)
    def _treinar_regressao(self):
        self.reg_features = ["chuva_7dias", "adubacao", "umidade_solo", "area_ha"]
        X = self.df[self.reg_features]
        y = self.df["produtividade"]
        self.regressao = LinearRegression()
        self.regressao.fit(X, y)
        self.reg_r2 = round(self.regressao.score(X, y), 3)

    def prever_regressao(self, chuva_7dias, adubacao, umidade_solo, area_ha):
        X = pd.DataFrame([[chuva_7dias, adubacao, umidade_solo, area_ha]], columns=self.reg_features)
        pred = float(self.regressao.predict(X)[0])
        coeficientes = dict(zip(self.reg_features, self.regressao.coef_.round(4)))
        return {
            "produtividade_prevista_ton_ha": round(max(pred, 0), 2),
            "coeficientes": coeficientes,
            "intercepto": round(float(self.regressao.intercept_), 4),
            "r2_treino": self.reg_r2,
        }

    # 5) APRIORI -> associacoes entre condicoes e ocorrencia de pragas
    def _treinar_apriori(self):
        transacoes = []
        for _, row in self.df.iterrows():
            itens = []
            itens.append("umidade_solo_baixa" if row.umidade_solo < 35 else ("umidade_solo_alta" if row.umidade_solo > 65 else "umidade_solo_media"))
            itens.append("temperatura_alta" if row.temperatura > 29 else "temperatura_normal")
            itens.append("umidade_ar_alta" if row.umidade_ar > 70 else "umidade_ar_normal")
            itens.append("chuva_baixa" if row.chuva_7dias < 15 else "chuva_normal")
            itens.append("historico_pragas_alto" if row.historico_pragas == 2 else "historico_pragas_baixo_medio")
            itens.append("ocorreu_praga" if row.praga_ocorrencia == 1 else "sem_praga")
            transacoes.append(itens)

        te = TransactionEncoder()
        te_array = te.fit(transacoes).transform(transacoes)
        df_trans = pd.DataFrame(te_array, columns=te.columns_)

        frequentes = apriori(df_trans, min_support=0.08, use_colnames=True)
        if len(frequentes) > 0:
            regras = association_rules(frequentes, metric="confidence", min_threshold=0.5, num_itemsets=len(frequentes))
            regras = regras[regras["consequents"].apply(lambda x: "ocorreu_praga" in x)]
            regras = regras.sort_values("confidence", ascending=False).head(8)
        else:
            regras = pd.DataFrame()

        self.apriori_frequentes = frequentes
        self.apriori_regras = regras

    def obter_apriori(self):
        itemsets = [
            {"itens": list(row["itemsets"]), "suporte": round(row["support"], 3)}
            for _, row in self.apriori_frequentes.sort_values("support", ascending=False).head(10).iterrows()
        ] if len(self.apriori_frequentes) else []

        regras = [
            {
                "se": list(row["antecedents"]),
                "entao": list(row["consequents"]),
                "suporte": round(row["support"], 3),
                "confianca": round(row["confidence"], 3),
                "lift": round(row["lift"], 3),
            }
            for _, row in self.apriori_regras.iterrows()
        ] if len(self.apriori_regras) else []

        return {"itens_frequentes": itemsets, "regras_associacao": regras}
