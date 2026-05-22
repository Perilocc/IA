# FarmaciaIA

Sistema de gestão farmacêutica com três camadas integradas:

- API principal para estoque, funcionários, fornecedores e vendas.
- Frontend em Streamlit para operação do sistema.
- Serviço RAG 2 com busca semântica, expansão de consulta e rerank.

O projeto também permite envio de documentos PDF, DOCX e TXT para indexação no RAG.

## Funcionalidades

- Cadastro e listagem de medicamentos.
- Gestão de funcionários.
- Cadastro de fornecedores.
- Registro de vendas.
- Upload de documentos para consulta pela IA.
- Assistente IA com recuperação semântica de trechos.
- Visualização dos chunks recuperados diretamente no frontend.

## Estrutura

- `app.py`: interface Streamlit.
- `api/`: backend principal da farmácia.
- `RAG/`: serviço de IA, embeddings, chat e indexação vetorial.
- `start.md`: comandos rápidos de execução.

## Requisitos

- Python 3.12 ou compatível com o ambiente virtual do projeto.
- Ollama instalado e rodando em `http://127.0.0.1:11434`.
- Modelos Ollama:
  - `gemma3`
  - `nomic-embed-text`

## Instalação

1. Crie e ative o ambiente virtual.
2. Instale as dependências.
3. Baixe os modelos do Ollama.

```bash
source venv/bin/activate
pip install -r requirements.txt
ollama pull gemma3
ollama pull nomic-embed-text
```

## Execução

Abra três terminais e inicie os serviços nesta ordem:

```bash
uvicorn api.main:app --reload --port 8000
uvicorn RAG.main:app --reload --port 8001
streamlit run app.py
```

## Fluxo do RAG 2

O assistente IA usa uma estratégia de recuperação semântica com reranking:

- Expansão da consulta.
- Busca semântica no Chroma.
- Rerank com `sentence-transformers`.
- Geração final com Ollama.

Se o reranker não estiver disponível, o sistema segue com os trechos recuperados.

## Upload de documentos

Na tela `Documentos`, o Streamlit aceita:

- PDF
- DOCX
- TXT

Os arquivos são enviados ao serviço RAG e indexados para uso no assistente.

## Endpoints principais

API principal:

- `GET /dashboard/`
- `GET /medicamentos/`
- `GET /funcionarios/`
- `GET /fornecedores/`
- `GET /vendas/`

RAG:

- `GET /ai/health`
- `POST /ai/sync`
- `POST /ai/chat`
- `POST /ai/documents/upload`

## Variáveis de ambiente

Você pode sobrescrever estes valores:

- `MAIN_API_URL`
- `OLLAMA_BASE_URL`
- `LLM_MODEL`
- `EMBED_MODEL`
- `CHROMA_PATH`

Exemplo:

```bash
export MAIN_API_URL=http://127.0.0.1:8000
export OLLAMA_BASE_URL=http://127.0.0.1:11434
export LLM_MODEL=gemma3
export EMBED_MODEL=nomic-embed-text
```

## Observações

- Se o Chroma persistido estiver inconsistente, o serviço usa fallback em memória para manter a API disponível.
- A visualização dos chunks recuperados aparece no assistente como um expander com ID e preview.
- O serviço RAG faz logging de falhas no Ollama e no processamento do chat para facilitar diagnóstico.

## Próximos passos sugeridos

- Cachear resultados da expansão de consulta para reduzir custo por pergunta.
- Exibir score de cada chunk na interface.
- Adicionar uma tela para histórico de uploads de documentos.