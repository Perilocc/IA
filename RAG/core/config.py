import os

AI_CONFIG = {
    "MAIN_API_URL": os.getenv(
        "MAIN_API_URL",
        "http://127.0.0.1:8000"
    ),

    "OLLAMA_URL": os.getenv(
        "OLLAMA_BASE_URL",
        "http://127.0.0.1:11434"
    ),

    "LLM_MODEL": os.getenv(
        "LLM_MODEL",
        "gemma3"
    ),

    "EMBED_MODEL": os.getenv(
        "EMBED_MODEL",
        "nomic-embed-text"
    ),

    "CHROMA_PATH": os.getenv(
        "CHROMA_PATH",
        "./ai_farmacia_index"
    )
}