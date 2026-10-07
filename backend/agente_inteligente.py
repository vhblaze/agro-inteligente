"""Agente Inteligente AgroAgente: percebe, raciocina (usando as demais tecnicas) e age."""


def decidir(fatos, resultado_especialista, resultado_fuzzy, resultado_arvore, resultado_knn, resultado_kmeans, resultado_regressao):
    """Combina as saidas de todas as tecnicas e produz a decisao final do agente."""

    motivos = []
    acoes = []

    # Irrigacao: prioriza o sistema especialista, reforcado pela fuzzy
    decisao_irrigacao = resultado_especialista["decisao_final"]
    necessidade_fuzzy = resultado_fuzzy["necessidade_irrigacao_rotulo"]
    if "rrigar" in decisao_irrigacao:
        acoes.append(f"Irrigar o talhao (nivel fuzzy de necessidade: {necessidade_fuzzy}, {resultado_fuzzy['necessidade_irrigacao_percentual']}%)")
        motivos.append(f"Sistema Especialista concluiu '{decisao_irrigacao}' e a Logica Fuzzy indica necessidade {necessidade_fuzzy.lower()} de irrigacao.")
    else:
        acoes.append(f"Nao irrigar agora (necessidade fuzzy: {necessidade_fuzzy}, {resultado_fuzzy['necessidade_irrigacao_percentual']}%)")
        motivos.append(f"Sistema Especialista concluiu '{decisao_irrigacao}', compativel com a necessidade {necessidade_fuzzy.lower()} apontada pela Logica Fuzzy.")

    # Risco de praga: combina KNN com regra do especialista
    risco_knn = resultado_knn["classificacao_risco_praga"]
    if risco_knn == "Alto" or "praga" in decisao_irrigacao.lower():
        acoes.append("Emitir alerta de risco de pragas e recomendar inspecao do talhao")
    motivos.append(f"O KNN classificou o risco de pragas como '{risco_knn}' com base nos talhoes mais semelhantes do historico.")

    # Irrigacao segundo a arvore de decisao
    motivos.append(f"A Arvore de Decisao classificou a necessidade de irrigacao como '{resultado_arvore['classificacao']}'.")

    # Perfil do talhao (K-Means)
    motivos.append(f"O K-Means posicionou o talhao no grupo '{resultado_kmeans['perfil']}' (Grupo {resultado_kmeans['cluster']}).")

    # Produtividade estimada
    produtividade = resultado_regressao["produtividade_prevista_ton_ha"]
    acoes.append(f"Produtividade estimada da safra: {produtividade} ton/ha")
    motivos.append(f"A Regressao Linear estimou produtividade de {produtividade} ton/ha para as condicoes informadas.")

    resumo = (
        f"Decisao do AgroAgente: {' | '.join(acoes)}."
    )

    return {
        "percepcao": fatos,
        "acoes_recomendadas": acoes,
        "justificativas": motivos,
        "resumo_decisao": resumo,
    }
