"""Gera o dataset sintetico de talhoes agricolas usado pelo AgroInteligente."""
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
N = 320
CULTURAS = ["Milho", "Soja", "Cafe", "Cana-de-acucar"]

def gerar_dataset():
    cultura = RNG.choice(CULTURAS, size=N)
    umidade_solo = np.clip(RNG.normal(45, 20, N), 5, 95)
    temperatura = np.clip(RNG.normal(26, 5, N), 10, 40)
    umidade_ar = np.clip(RNG.normal(60, 15, N), 20, 95)
    chuva_7dias = np.clip(RNG.exponential(20, N), 0, 120)
    dias_sem_irrigar = RNG.integers(0, 15, N)
    adubacao = np.clip(RNG.normal(180, 60, N), 20, 350)
    area_ha = np.round(np.clip(RNG.normal(12, 6, N), 1, 40), 1)
    historico_pragas = RNG.choice([0, 1, 2], size=N, p=[0.5, 0.3, 0.2])  # 0 baixo 1 medio 2 alto

    # praga ocorre mais quando umidade do ar alta + temperatura alta + historico alto
    prob_praga = (
        0.1
        + 0.35 * (umidade_ar > 70)
        + 0.25 * (temperatura > 29)
        + 0.25 * (historico_pragas == 2)
    )
    praga_ocorrencia = (RNG.random(N) < np.clip(prob_praga, 0, 0.9)).astype(int)

    # produtividade depende de chuva, adubacao, umidade do solo e inversamente de praga
    produtividade = (
        2.0
        + 0.03 * chuva_7dias
        + 0.012 * adubacao
        + 0.02 * umidade_solo
        - 1.3 * praga_ocorrencia
        + RNG.normal(0, 0.6, N)
    )
    produtividade = np.round(np.clip(produtividade, 0.5, 14), 2)

    df = pd.DataFrame({
        "cultura": cultura,
        "umidade_solo": np.round(umidade_solo, 1),
        "temperatura": np.round(temperatura, 1),
        "umidade_ar": np.round(umidade_ar, 1),
        "chuva_7dias": np.round(chuva_7dias, 1),
        "dias_sem_irrigar": dias_sem_irrigar,
        "adubacao": np.round(adubacao, 1),
        "area_ha": area_ha,
        "historico_pragas": historico_pragas,
        "praga_ocorrencia": praga_ocorrencia,
        "produtividade": produtividade,
    })

    # rotulo de necessidade de irrigacao (usado pela arvore de decisao)
    def classifica_irrigacao(row):
        if row.umidade_solo < 30 and row.chuva_7dias < 15:
            return "Alta"
        if row.umidade_solo < 50:
            return "Media"
        return "Baixa"

    df["necessidade_irrigacao"] = df.apply(classifica_irrigacao, axis=1)

    # rotulo de risco de praga (usado pelo KNN)
    def classifica_risco_praga(row):
        score = (row.umidade_ar > 70) + (row.temperatura > 29) + (row.historico_pragas == 2)
        if score >= 2:
            return "Alto"
        if score == 1:
            return "Medio"
        return "Baixo"

    df["risco_praga"] = df.apply(classifica_risco_praga, axis=1)

    return df


if __name__ == "__main__":
    dataset = gerar_dataset()
    dataset.to_csv("data/talhoes.csv", index=False, encoding="utf-8")
    print(f"Dataset gerado com {len(dataset)} registros em data/talhoes.csv")
