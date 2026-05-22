import chromadb
from chromadb.config import Settings
from RAG.core.config import AI_CONFIG


client = chromadb.PersistentClient(
    path=AI_CONFIG["CHROMA_PATH"],
    settings=Settings(
        anonymized_telemetry=False
    )
)

collection = client.get_or_create_collection(
    name="farmacia_rag",
    metadata={
        "hnsw:space": "cosine"
    }
)