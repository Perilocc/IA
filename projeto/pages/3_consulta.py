from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
import pandas as pd
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("💬 Consulta Inteligente Jurídica")

try:
    df = pd.read_json("dados_processados.json")

except FileNotFoundError:
    st.warning("Nenhum dado processado encontrado.")
    st.stop()

pergunta = st.chat_input(
    "Faça uma pergunta sobre os processos analisados na Triagem:"
)

if pergunta:
    if not pergunta.strip():
        st.warning("Digite uma pergunta.")
        st.stop()

    prompt = f"""
    Base de dados processada:
    
    {df.to_json(orient="records", force_ascii=False)}

    Pergunta do usuário:
    {pergunta}
    """

    with st.spinner("Consultando IA..."):
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
                    Você é um assistente jurídico analítico.

                    Responda SOMENTE com base nos dados fornecidos.

                    Sempre que possível:
                    - cite os processos encontrados;
                    - apresente os dados de forma estruturada;
                    - inclua número do processo;
                    - inclua categoria;
                    - inclua prioridade;
                    - inclua complexidade;
                    - inclua risco financeiro.

                    Se a pergunta envolver listagem ou análise:
                    - organize a resposta em tópicos;
                    - seja claro e objetivo.

                    Se a informação não estiver presente:
                    - diga que não há dados suficientes;
                    - não invente informações;
                    - não faça suposições.

                    Nunca responda usando conhecimento externo.
                    Seja objetivo e profissional.
                    """
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1
        )

        st.subheader("📄 Resposta da IA")
        st.markdown(resp.choices[0].message.content)