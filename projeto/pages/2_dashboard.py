from graphs.risco_financeiro_graph import gerar_grafico_risco_financeiro
from graphs.complexidade_graph import gerar_grafico_complexidade
from graphs.prioridade_graph import gerar_grafico_prioridade
from graphs.categoria_graph import gerar_grafico_categoria
from prompts.dashboard_prompt import PROMPT_DASHBOARD
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
import pandas as pd
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("📊 Dashboard Analítico Jurídico")

try:
    df = pd.read_json("dados_processados.json")
    
    st.subheader("📌 Resumo Geral")
    col1, col2, col3 = st.columns(3)
    
    col1.metric(
        "Total de Processos",
        len(df)
    )
    col2.metric(
        "Prioridade Média",
        f"{df['prioridade'].astype(float).mean():.1f}"
    )
    col3.metric(
        "Categorias",
        df['categoria'].nunique()
    )
    
    st.pyplot(
        gerar_grafico_categoria(df)
    )
    st.pyplot(
        gerar_grafico_prioridade(df)
    )
    st.pyplot(
        gerar_grafico_complexidade(df)
    )
    st.pyplot(
        gerar_grafico_risco_financeiro(df)
    )
    
    prompt_completo = f"""
        {PROMPT_DASHBOARD}

        Dados Processados:
        {df.to_string(index=False)}
    """
    st.divider()
    st.subheader("🤖 Insights Estratégicos com IA")
    st.info(
        """
        Gere um relatório executivo automático com análise estratégica
        dos processos jurídicos processados pela IA.
        """
    )
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        gerar_relatorio = st.button(
            "📄 Gerar Relatório Executivo",
            use_container_width=True
        )

    if gerar_relatorio:
        with st.spinner("Gerando análise estratégica..."):
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Você é um analista jurídico estratégico. "
                            "Seja objetivo, analítico e profissional."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt_completo
                    }
                ],
                temperature=0.3
            )
            
            relatorio = resp.choices[0].message.content
            st.success("✅ Relatório Executivo Gerado")
            
            with st.expander("📑 Visualizar Relatório", expanded=True):
                st.markdown(relatorio)

except FileNotFoundError:
    st.warning("Nenhum dado processado encontrado.")
    st.stop()