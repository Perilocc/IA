from RAG.core.logging_config import logger
from RAG.core.config import AI_CONFIG
import httpx


async def check_ollama_health() -> bool:
    """Verifica se o Ollama está acessível."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{AI_CONFIG['OLLAMA_URL']}/api/tags")
            return resp.status_code == 200
    except:
        return False


async def get_embeddings(texts):
    async with httpx.AsyncClient(
        timeout=60
    ) as client:

        response=await client.post(
            f"{AI_CONFIG['OLLAMA_URL']}/api/embed",
            json={
                "model":AI_CONFIG["EMBED_MODEL"],
                "input":texts
            }
        )

        response.raise_for_status()
        return response.json()["embeddings"]


async def generate(prompt):
    async with httpx.AsyncClient(
        timeout=90
    ) as client:

        response=await client.post(
            f"{AI_CONFIG['OLLAMA_URL']}/api/generate",
            json={
                "model":AI_CONFIG["LLM_MODEL"],
                "prompt":prompt,
                "stream":False
            }
        )

        response.raise_for_status()
        return response.json()[
            "response"
        ]