import chromadb
from chromadb.config import Settings

from RAG.core.config import AI_CONFIG
from RAG.core.logging_config import logger


def _build_client():
    try:
        return chromadb.PersistentClient(
            path=AI_CONFIG["CHROMA_PATH"],
            settings=Settings(
                anonymized_telemetry=False
            )
        )
    except BaseException as exc:
        logger.warning(
            "Falha ao iniciar Chroma persistente em %s: %s. Usando memória temporária.",
            AI_CONFIG["CHROMA_PATH"],
            exc,
        )
        return chromadb.Client(
            settings=Settings(
                anonymized_telemetry=False
            )
        )


client = _build_client()

collection = client.get_or_create_collection(
    name="farmacia_rag",
    metadata={
        "hnsw:space": "cosine"
    }
)