"""Sistema Especialista baseado em regras SE-ENTAO para o AgroInteligente."""


def avaliar(dados):
    """Recebe os fatos do talhao e retorna as regras ativadas + conclusao final.

    dados: dict com umidade_solo, temperatura, umidade_ar, chuva_7dias,
           chuva_prevista (bool), historico_pragas (0,1,2)
    """
    umidade_solo = dados["umidade_solo"]
    temperatura = dados["temperatura"]
    umidade_ar = dados["umidade_ar"]
    chuva_7dias = dados["chuva_7dias"]
    chuva_prevista = dados.get("chuva_prevista", False)
    historico_pragas = dados.get("historico_pragas", 0)

    regras_ativadas = []
    conclusoes = []

    # Regra 1
    if umidade_solo < 30 and temperatura > 28:
        regras_ativadas.append("SE umidade_solo < 30% E temperatura > 28C ENTAO irrigar com urgencia")
        conclusoes.append("Irrigar com urgencia")

    # Regra 2
    if umidade_solo < 30 and not chuva_prevista:
        regras_ativadas.append("SE umidade_solo < 30% E NAO ha previsao de chuva ENTAO irrigar")
        conclusoes.append("Irrigar")

    # Regra 3
    if 30 <= umidade_solo <= 60:
        regras_ativadas.append("SE umidade_solo entre 30% e 60% ENTAO monitorar solo")
        conclusoes.append("Monitorar")

    # Regra 4
    if umidade_solo > 60 or chuva_7dias > 50:
        regras_ativadas.append("SE umidade_solo > 60% OU chuva acumulada > 50mm ENTAO nao irrigar")
        conclusoes.append("Nao irrigar")

    # Regra 5
    if temperatura > 32 and umidade_ar < 40:
        regras_ativadas.append("SE temperatura > 32C E umidade_ar < 40% ENTAO risco de estresse hidrico alto")
        conclusoes.append("Alerta: estresse hidrico")

    # Regra 6
    if historico_pragas == 2 and umidade_ar > 70:
        regras_ativadas.append("SE historico_pragas e ALTO E umidade_ar > 70% ENTAO recomendar inspecao de pragas")
        conclusoes.append("Inspecionar pragas")

    # Regra 7
    if chuva_7dias > 50:
        regras_ativadas.append("SE chuva acumulada (7 dias) > 50mm ENTAO suspender irrigacao programada")
        conclusoes.append("Suspender irrigacao")

    if not regras_ativadas:
        regras_ativadas.append("Nenhuma regra critica ativada ENTAO manter rotina padrao")
        conclusoes.append("Rotina padrao")

    decisao_final = conclusoes[0] if conclusoes else "Rotina padrao"

    return {
        "fatos": dados,
        "regras_ativadas": regras_ativadas,
        "conclusoes": conclusoes,
        "decisao_final": decisao_final,
        "mecanismo_inferencia": "Encadeamento para frente (forward chaining) - avalia todas as regras contra os fatos e acumula as conclusoes",
    }
