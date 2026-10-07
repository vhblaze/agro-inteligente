# AgroInteligente — Trabalho V1 (Inteligência Artificial)

Sistema inteligente de apoio à decisão agrícola que integra **Agente Inteligente**,
**Sistema Especialista**, **Lógica Fuzzy** e **5 algoritmos de Machine Learning**
(Árvore de Decisão, KNN, K-Means, Regressão Linear e Apriori).

Documento completo do trabalho (Etapas 1 a 6) para entrega: [`docs/Projeto_AgroInteligente_V1.docx`](docs/Projeto_AgroInteligente_V1.docx)

## Estrutura do projeto

```
backend/
  app.py                 -> API Flask que integra todas as tecnicas
  sistema_especialista.py-> regras SE/ENTAO (Etapa 3)
  logica_fuzzy.py         -> logica fuzzy manual (Etapa 4)
  machine_learning.py     -> Arvore, KNN, K-Means, Regressao, Apriori (Etapa 5)
  agente_inteligente.py   -> AgroAgente, integra tudo (Etapas 2 e 6)
  data_generator.py       -> gera o dataset sintetico de talhoes
  data/talhoes.csv        -> dataset usado pelos modelos
  requirements.txt
frontend/
  index.html / style.css / script.js  -> interface web
docs/
  Projeto_AgroInteligente_V1.docx     -> documento para entregar a professora
```

## Como executar

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python data_generator.py     # gera backend/data/talhoes.csv
python app.py
```

Acesse **http://127.0.0.1:5000** no navegador. O Flask já serve o frontend
junto com a API (não é necessário rodar um servidor separado para o `frontend/`).

## Fluxo da aplicação

1. O usuário informa as condições do talhão (umidade do solo, temperatura,
   umidade do ar, chuva, adubação, área e histórico de pragas).
2. O backend roda, em sequência: Sistema Especialista → Lógica Fuzzy →
   Árvore de Decisão → KNN → K-Means → Regressão Linear → Apriori.
3. O **AgroAgente** consolida todos os resultados em uma recomendação final
   (irrigar ou não, alerta de pragas, produtividade estimada e perfil do talhão).
4. A interface exibe cada técnica em um cartão próprio e a decisão final em destaque.
