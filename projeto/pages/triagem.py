from prompts.triagem_prompt import PROMPT_TRIAGEM
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
import pandas as pd
import json, os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("📈 Triagem e Análise de Processos Jurídicos")

processos = st.text_area(
    "Cole os detalhes dos processos jurídicos em formato JSON:"
)

if st.button("Fazer Análise e Triagem de Processos"):
    if not processos.strip():
        st.warning("Insira os processos em formato json.")
        st.stop()
    
    try:
        processos_json = json.loads(processos)
    except json.JSONDecodeError:
        st.error("JSON inválido. Verifique a estrutura enviada.")
        st.stop()
    
    prompt_completo = f"""
    {PROMPT_TRIAGEM}

    Processos:
    {json.dumps(processos_json, ensure_ascii=False, indent=2)}
    """

    with st.spinner("Processando com IA..."):
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um especialista em análise de processos jurídicos. "
                        "Retorne apenas JSON válido, sem markdown."
                    )
                },
                {
                    "role": "user",
                    "content": prompt_completo
                }
            ],
            temperature=0.2
        )
        
        try:
            result = json.loads(resp.choices[0].message.content)
            
            # Garantir que o resultado seja uma lista de processos
            dados_processados = result if isinstance(result, list) else [result]
            
            df = pd.DataFrame(dados_processados).fillna("N/A")
            df.to_json(
                "dados_processados.json",
                orient="records",
                force_ascii=False,
                indent=4
            )

            st.subheader("📋 Processos Triados")
            
            for idx, proc in enumerate(dados_processados):
                
                with st.expander(f"Processo {idx + 1} - {proc.get('categoria', 'N/A')}", expanded=True):
                    col1, col2, col3 = st.columns(3)

                    col1.metric("Prioridade", f"{proc.get('prioridade', 0)}/5")
                    col2.metric("Complexidade", proc.get('complexidade', 'N/A'))
                    col3.metric("Risco Financeiro", proc.get('risco_financeiro', 'N/A'))

                    st.write(
                        f"**Processo:** "
                        f"{proc.get('processo', 'N/A')}"
                    )

                    st.write(
                        f"**Categoria Jurídica:** "
                        f"{proc.get('categoria', 'N/A')}"
                    )

                    st.info(
                        f"**Rascunho Jurídico:** "
                        f"{proc.get('resposta_rascunho', 'Sem resumo disponível.')}"
                    )

            st.subheader("📊 Visão Geral da Triagem")
            
            st.table(
                df[
                    [
                        'processo',
                        'categoria',
                        'prioridade',
                        'complexidade',
                        'risco_financeiro'
                    ]
                ]
            )
            
            st.subheader("📌 Resumo Geral")
            col1, col2, col3 = st.columns(3)
            
            col1.metric(
                "Quantidade de Processos",
                len(df)
            )

            col2.metric(
                "Prioridade Média",
                f"{df['prioridade'].astype(float).mean():.1f}"
            )

            col3.metric(
                "Categorias Encontradas",
                df['categoria'].nunique()
            )
        except Exception as e:
            st.error(f"Erro ao processar resposta da IA: {e}")

            st.subheader("Resposta bruta da IA")
            st.code(resp.choices[0].message.content)