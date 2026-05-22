# 1 - Instalar o Modelo Ollama

> Baixe os modelos necessários (CPU/GPU compatível)
 ollama pull gemma3
 ollama pull nomic-embed-text

> Verifique se o serviço está rodando na porta 11434
 curl http://localhost:11434/api/tags

# 2 - Rodar o Projeto

# Terminal 1: API Principal (Farmácia)
uvicorn api.main:app --reload --port 8000

# Terminal 2: Serviço de IA (RAG)
uvicorn RAG.main:app --reload --port 8001

# Terminal 3: Frontend Streamlit
streamlit run app.py
