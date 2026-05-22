from RAG.utils.chunker import chunk_documents
from RAG.services.ollama_service import (
    get_embeddings,
    check_ollama_health
)
from RAG.core.logging_config import logger
from RAG.core.chroma import collection
from RAG.core.config import AI_CONFIG
from fastapi import HTTPException
from datetime import datetime
import httpx
import time

last_sync = None
sync_in_progress = False

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

async def sync_index():
    global last_sync
    global sync_in_progress

    if sync_in_progress:
        raise HTTPException(
            status_code=429,
            detail="Sincronização já em andamento"
        )

    if not await check_ollama_health():
        raise HTTPException(
            status_code=503,
            detail="Ollama indisponível"
        )

    sync_in_progress = True
    start = time.time()

    try:
        logger.info(
            "Iniciando sincronização..."
        )
        data = await fetch_main_data()
        
        if not any(data.values()):
            raise HTTPException(
                status_code=502,
                detail="Banco vazio"
            )

        chunks, ids, metadatas = chunk_documents(
            data
        )

        if not chunks:
            last_sync = datetime.now().isoformat()
            return {
                "status":"success",
                "indexed":0,
                "message":"Sem dados",
                "last_sync":last_sync
            }

        existing = collection.get(
            ids=ids
        )

        if existing["ids"]:
            collection.delete(
                ids=existing["ids"]
            )

        embeddings = await get_embeddings(
            chunks
        )

        collection.upsert(
            documents=chunks,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )

        elapsed = time.time() - start
        last_sync = datetime.now().isoformat()
        logger.info(
            f"Sincronizado em {elapsed:.1f}s"
        )

        return {
            "status":"success",
            "indexed":len(chunks),
            "message":f"Concluído em {elapsed:.1f}s",
            "last_sync":last_sync
        }

    except Exception as e:
        logger.error(
            f"Erro: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        sync_in_progress=False