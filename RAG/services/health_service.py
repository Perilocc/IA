from RAG.core.chroma import collection

from RAG.services.ollama_service import (
    check_ollama_health
)

from RAG.services.sync_service import (
    last_sync
)

async def health_check():
    ollama_ok = await check_ollama_health()
    return {
        "status": "healthy" if ollama_ok else "degraded",
        "ollama": "connected" if ollama_ok else "disconnected",
        "indexed_docs": collection.count(),
        "last_sync": last_sync
    }