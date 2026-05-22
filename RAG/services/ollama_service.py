from RAG.core.config import AI_CONFIG
from RAG.core.logging_config import logger
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
        try:
            response = await client.post(
                f"{AI_CONFIG['OLLAMA_URL']}/api/embed",
                json={
                    "model": AI_CONFIG["EMBED_MODEL"],
                    "input": texts,
                },
            )
            response.raise_for_status()
            payload = response.json()
            return payload["embeddings"]
        except httpx.HTTPStatusError as exc:
            logger.exception(
                "Falha ao gerar embeddings com o Ollama (status %s): %s",
                exc.response.status_code,
                exc.response.text,
            )
            raise
        except Exception:
            logger.exception("Falha inesperada ao gerar embeddings com o Ollama")
            raise


async def generate(prompt):
    async with httpx.AsyncClient(
        timeout=90
    ) as client:
        try:
            response = await client.post(
                f"{AI_CONFIG['OLLAMA_URL']}/api/generate",
                json={
                    "model": AI_CONFIG["LLM_MODEL"],
                    "prompt": prompt,
                    "stream": False,
                },
            )
            response.raise_for_status()
            return response.json()["response"]
        except httpx.HTTPStatusError as exc:
            logger.exception(
                "Falha ao gerar resposta com o Ollama usando o modelo %s (status %s): %s",
                AI_CONFIG["LLM_MODEL"],
                exc.response.status_code,
                exc.response.text,
            )
            raise
        except Exception:
            logger.exception(
                "Falha inesperada ao gerar resposta com o Ollama usando o modelo %s",
                AI_CONFIG["LLM_MODEL"],
            )
            raise