# api_ai_farmacia.py
import os, json, logging, time
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import chromadb
from chromadb.config import Settings
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURAÇÃO & LOGGING
# ─────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("farmacia-ai")

AI_CONFIG = {
    "MAIN_API_URL": os.getenv("MAIN_API_URL", "http://127.0.0.1:8002"),
    "OLLAMA_URL": os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
    "LLM_MODEL": os.getenv("LLM_MODEL", "gemma3"),
    "EMBED_MODEL": os.getenv("EMBED_MODEL", "nomic-embed-text"),
    "CHROMA_PATH": os.getenv("CHROMA_PATH", "./ai_farmacia_index"),
}

app = FastAPI(title="Farmácia AI Service (RAG)", version="1.0")

# VectorDB local
client = chromadb.PersistentClient(
    path=AI_CONFIG["CHROMA_PATH"],
    settings=Settings(anonymized_telemetry=False)
)

collection = client.get_or_create_collection(
    name="farmacia_rag",
    metadata={"hnsw:space": "cosine"}
)

last_sync = None
sync_in_progress = False

# ─────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────
class ChatRequest(BaseModel):
    query: str
    top_k: int = 4

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    status: str = "success"
    processing_time: float = 0.0

class SyncStatus(BaseModel):
    status: str
    indexed: int
    message: str
    last_sync: Optional[str] = None

# ─────────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────
async def check_ollama_health() -> bool:
    """Verifica se o Ollama está acessível."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{AI_CONFIG['OLLAMA_URL']}/api/tags")
            return resp.status_code == 200
    except:
        return False

async def fetch_main_data():
    """Busca dados da API principal da Farmácia."""
    async with httpx.AsyncClient(timeout=15.0) as http:
        endpoints = ["/medicamentos/", "/funcionarios/", "/fornecedores/", "/vendas/"]
        data = {}
        for ep in endpoints:
            try:
                resp = await http.get(f"{AI_CONFIG['MAIN_API_URL']}{ep}")
                resp.raise_for_status()
                key = ep.strip("/")
                data[key] = resp.json().get(key, [])
                logger.info(f"✓ Buscados {len(data[key])} registros de {key}")
            except Exception as e:
                logger.warning(f"✗ Falha ao buscar {ep}: {e}")
                data[key] = []
        return data

def chunk_documents(data: dict):
    """Transforma os registros da Farmácia em documentos otimizados para busca semântica."""
    chunks, ids, metadatas = [], [], []
    
    for module, records in data.items():
        for rec in records:
            if module == "medicamentos":
                doc_text = f"Medicamento: {rec.get('nome')}. Categoria: {rec.get('categoria', 'N/A')}. Preço: R${rec.get('preco')}. Estoque atual: {rec.get('estoque')} unidades. Validade: {rec.get('validade', 'N/A')}."
            elif module == "funcionarios":
                doc_text = f"Funcionário: {rec.get('nome')}. Cargo: {rec.get('cargo')}. Status: {rec.get('status')}. Telefone: {rec.get('telefone', 'N/A')}."
            elif module == "fornecedores":
                doc_text = f"Fornecedor: {rec.get('empresa')}. CNPJ: {rec.get('cnpj')}. Contato: {rec.get('telefone', 'N/A')}."
            elif module == "vendas":
                # Utilizando os joins que já vêm da sua API de vendas
                doc_text = f"Venda registrada em {rec.get('data_venda')}. Medicamento vendido: {rec.get('medicamento', 'ID '+str(rec.get('medicamento_id')))} ({rec.get('quantidade')} unidades). Valor total: R${rec.get('valor_total')}. Venda realizada pelo funcionário: {rec.get('funcionario', 'ID '+str(rec.get('funcionario_id')))}."
            else:
                doc_text = json.dumps(rec, ensure_ascii=False)
            
            chunk_id = f"{module}_{rec.get('id', 'unknown')}"
            chunks.append(doc_text)
            ids.append(chunk_id)
            metadatas.append({
                "module": module,
                "record_id": str(rec.get('id', 'unknown')),
            })
    
    return chunks, ids, metadatas

async def get_ollama_embeddings(texts: List[str]) -> List[List[float]]:
    """Gera embeddings via Ollama."""
    if not texts:
        return []
    
    async with httpx.AsyncClient(timeout=60.0) as http:
        try:
            resp = await http.post(
                f"{AI_CONFIG['OLLAMA_URL']}/api/embed",
                json={"model": AI_CONFIG["EMBED_MODEL"], "input": texts}
            )
            resp.raise_for_status()
            return resp.json()["embeddings"]
        except Exception as e:
            logger.error(f"Erro no embedding: {e}")
            return [[0.0] * 768] * len(texts)

async def generate_with_ollama(prompt: str) -> str:
    """Gera resposta via Ollama usando /api/generate"""
    async with httpx.AsyncClient(timeout=90.0) as http:
        try:
            resp = await http.post(
                f"{AI_CONFIG['OLLAMA_URL']}/api/generate",
                json={
                    "model": AI_CONFIG["LLM_MODEL"],
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2, # Temperatura baixa para dados de saúde/farmácia (menos alucinação)
                        "num_predict": 600
                    }
                }
            )
            resp.raise_for_status()
            return resp.json()["response"]
        except Exception as e:
            logger.error(f"Erro na geração: {e}")
            raise HTTPException(status_code=500, detail=f"Erro ao gerar resposta: {str(e)}")

# ─────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────
@app.post("/ai/sync", response_model=SyncStatus)
async def sync_index():
    """Sincroniza os dados do banco SQLite da Farmácia e atualiza o índice vetorial."""
    global last_sync, sync_in_progress
    
    if sync_in_progress:
        raise HTTPException(status_code=429, detail="Sincronização já em andamento")
    
    if not await check_ollama_health():
        raise HTTPException(status_code=503, detail="Ollama não está acessível. Verifique se está rodando.")
    
    sync_in_progress = True
    start_time = time.time()
    
    try:
        logger.info("🔄 Iniciando sincronização da Farmácia...")
        data = await fetch_main_data()
        
        if not any(data.values()):
            raise HTTPException(status_code=502, detail="API principal indisponível ou banco vazio.")
        
        chunks, ids, metadatas = chunk_documents(data)
        
        if not chunks:
            last_sync = datetime.now().isoformat()
            return SyncStatus(status="success", indexed=0, message="Sem dados para indexar", last_sync=last_sync)
        
        logger.info(f"📊 Processando {len(chunks)} documentos...")
        
        existing = collection.get(ids=ids)
        if existing["ids"]:
            collection.delete(ids=existing["ids"])
        
        embeddings = await get_ollama_embeddings(chunks)
        collection.upsert(documents=chunks, embeddings=embeddings, ids=ids, metadatas=metadatas)
        
        elapsed = time.time() - start_time
        last_sync = datetime.now().isoformat()
        logger.info(f"✅ Índice atualizado em {elapsed:.1f}s")
        
        return SyncStatus(
            status="success",
            indexed=len(chunks),
            message=f"Sincronização concluída em {elapsed:.1f}s",
            last_sync=last_sync
        )
        
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        sync_in_progress = False

@app.post("/ai/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Endpoint de consulta RAG focado em Gestão Farmacêutica."""
    start_time = time.time()
    
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query obrigatória")
    
    if not await check_ollama_health():
        return ChatResponse(
            answer="🔌 Ollama não está acessível. Verifique se está rodando.",
            sources=[], status="error", processing_time=time.time() - start_time
        )
    
    try:
        q_emb = await get_ollama_embeddings([req.query])
        
        results = collection.query(
            query_embeddings=q_emb,
            n_results=min(req.top_k, 6),
            include=["documents", "metadatas"]
        )
        
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        
        if not docs:
            return ChatResponse(
                answer="📊 Nenhum dado no VectorDB. Execute /ai/sync primeiro.",
                sources=[], status="no_data", processing_time=time.time() - start_time
            )
        
        context_str = "\n".join([
            f"[{i+1}] [{m.get('module').upper()} ID:{m.get('record_id')}] - {d}"
            for i, (d, m) in enumerate(zip(docs, metas))
        ])
        
        prompt = f"""Você é o Assistente Especialista de Gestão e Crise da Farmácia.
Seu objetivo é analisar os dados internos do sistema e responder dúvidas operacionais, de estoque ou de equipe em português.

Contexto disponível no banco de dados corporativo:
{context_str}

Pergunta do Usuário: {req.query}

Instruções Cruciais:
- Use EXCLUSIVAMENTE os dados listados no contexto acima para formular a resposta.
- Se o contexto não tiver a informação para responder completamente, avise de forma direta.
- Quando citar um medicamento, venda ou funcionário, inclua a tag do ID no formato [ID:X] para referência.
- Seja claro, profissional e objetivo, ideal para um cenário de operação rápida.

Resposta:"""
        
        raw_answer = await generate_with_ollama(prompt)
        
        import re
        cited_ids = list(set(re.findall(r"ID[:\s]*([A-Za-z0-9_]+)", raw_answer)))
        valid_ids = [f"{m.get('module')}_{m.get('record_id')}" for m in metas if m.get("record_id") in cited_ids]
        
        return ChatResponse(
            answer=raw_answer,
            sources=valid_ids if valid_ids else [f"{m.get('module')}_{m.get('record_id')}" for m in metas[:3]],
            status="success",
            processing_time=time.time() - start_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro na consulta: {e}")
        return ChatResponse(
            answer=f"⚠️ Erro interno ao processar a pergunta.",
            sources=[], status="error", processing_time=time.time() - start_time
        )

@app.get("/ai/health")
async def health_check():
    """Verifica saúde do serviço de IA."""
    ollama_ok = await check_ollama_health()
    
    health = {
        "status": "healthy" if ollama_ok else "degraded",
        "ollama": "connected" if ollama_ok else "disconnected",
        "indexed_docs": collection.count(),
        "last_sync": last_sync,
        "ollama_url": AI_CONFIG["OLLAMA_URL"]
    }
    
    return health

if __name__ == "__main__":
    import uvicorn
    # Rodando o serviço de IA na porta 8003 para não conflitar com a API principal
    uvicorn.run(app, host="0.0.0.0", port=8003)