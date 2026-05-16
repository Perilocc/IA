import streamlit as st

st.set_page_config(
    page_title="Sistema Inteligente de Triagem Jurídica",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Sistema Inteligente de Triagem e Análise Jurídica")

st.markdown("""
Bem-vindo ao sistema de triagem jurídica inteligente utilizando Inteligência Artificial.

Este projeto realiza:

- 📋 Triagem automática de processos jurídicos
- 🧠 Classificação inteligente por categoria
- 🚨 Definição de prioridade processual
- 📊 Análise de complexidade dos casos
- 💰 Avaliação de risco financeiro
- 📈 Dashboard analítico com visualização de dados
- 🤖 Geração de insights estratégicos com IA

---

## 🧭 Como utilizar

### 1. Página de Triagem
Na página **📋 Triagem**, cole os processos jurídicos em formato JSON para que a IA realize a classificação automática.

A IA irá:
- identificar a categoria jurídica;
- calcular prioridade;
- classificar complexidade;
- avaliar risco financeiro;
- gerar um breve resumo jurídico.

---

### 2. Página de Dashboard
Na página **📊 Dashboard**, visualize:
- métricas gerais;
- distribuição de categorias;
- prioridades;
- complexidade;
- risco financeiro;
- relatório executivo estratégico gerado por IA.

---

### 3. Página de Consulta
Na página **💬 Consulta**, faça perguntas específicas sobre os processos analisados. 
A IA responderá com base nas informações disponíveis.
- Exemplo de perguntas:
    - "Quantos processos de Direito do Trabalho foram classificados como alta prioridade?"
    - "Qual é a distribuição de complexidade dos casos de Direito Civil?"
    - "Quais processos apresentam alto risco financeiro?"

## 🛠️ Tecnologias Utilizadas

- Python
- Streamlit
- Pandas
- Matplotlib
- OpenAI API

---

## 🎯 Objetivo do Projeto

Demonstrar a aplicação de Inteligência Artificial Generativa
na automação de triagem e análise estratégica de processos jurídicos.
""")