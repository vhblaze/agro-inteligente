"""Modulo de Logica Fuzzy (implementacao manual, sem dependencias externas).

Variaveis de entrada: umidade_solo (%) e temperatura (C)
Variavel de saida: necessidade_irrigacao (%)
"""


def _triangular(x, a, b, c):
    if x <= a or x >= c:
        return 0.0
    if x == b:
        return 1.0
    if x < b:
        return (x - a) / (b - a)
    return (c - x) / (c - b)


def _trapezoidal(x, a, b, c, d):
    if x <= a or x >= d:
        return 0.0
    if b <= x <= c:
        return 1.0
    if x < b:
        return (x - a) / (b - a)
    return (d - x) / (d - c)


def fuzzificar_umidade(umidade_solo):
    return {
        "baixa": _trapezoidal(umidade_solo, 0, 0, 20, 45),
        "media": _triangular(umidade_solo, 25, 50, 75),
        "alta": _trapezoidal(umidade_solo, 55, 80, 100, 100),
    }


def fuzzificar_temperatura(temperatura):
    return {
        "fria": _trapezoidal(temperatura, 0, 0, 15, 22),
        "amena": _triangular(temperatura, 18, 25, 32),
        "quente": _trapezoidal(temperatura, 28, 35, 45, 45),
    }


def avaliar(umidade_solo, temperatura):
    pert_umidade = fuzzificar_umidade(umidade_solo)
    pert_temp = fuzzificar_temperatura(temperatura)

    regras = [
        # (umidade, temperatura, saida, peso)
        ("baixa", "quente", "alta", min(pert_umidade["baixa"], pert_temp["quente"])),
        ("baixa", "amena", "alta", min(pert_umidade["baixa"], pert_temp["amena"])),
        ("baixa", "fria", "media", min(pert_umidade["baixa"], pert_temp["fria"])),
        ("media", "quente", "media", min(pert_umidade["media"], pert_temp["quente"])),
        ("media", "amena", "media", min(pert_umidade["media"], pert_temp["amena"])),
        ("media", "fria", "baixa", min(pert_umidade["media"], pert_temp["fria"])),
        ("alta", "quente", "media", min(pert_umidade["alta"], pert_temp["quente"])),
        ("alta", "amena", "baixa", min(pert_umidade["alta"], pert_temp["amena"])),
        ("alta", "fria", "baixa", min(pert_umidade["alta"], pert_temp["fria"])),
    ]

    regras_ativadas = [
        {
            "regra": f"SE umidade e {u.upper()} E temperatura e {t.upper()} ENTAO necessidade de irrigacao e {s.upper()}",
            "forca": round(peso, 3),
        }
        for (u, t, s, peso) in regras
        if peso > 0
    ]

    # centroides representativos de cada conjunto de saida (0-100%)
    centro_saida = {"baixa": 15, "media": 50, "alta": 85}

    numerador = sum(peso * centro_saida[s] for (_, _, s, peso) in regras)
    denominador = sum(peso for (_, _, _, peso) in regras)
    necessidade = round(numerador / denominador, 1) if denominador > 0 else 0.0

    if necessidade < 35:
        rotulo = "Baixa"
    elif necessidade < 65:
        rotulo = "Media"
    else:
        rotulo = "Alta"

    return {
        "pertinencia_umidade": {k: round(v, 3) for k, v in pert_umidade.items()},
        "pertinencia_temperatura": {k: round(v, 3) for k, v in pert_temp.items()},
        "regras_ativadas": regras_ativadas,
        "necessidade_irrigacao_percentual": necessidade,
        "necessidade_irrigacao_rotulo": rotulo,
    }
