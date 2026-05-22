import re
import time

from fastapi import HTTPException

from RAG.core.chroma import collection
from RAG.core.logging_config import logger

from RAG.services.ollama_service import (
    get_embeddings,
    generate,
    check_ollama_health
)


async def process_chat(req):
    start_time=time.time()

    if not req.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query obrigatória"
        )

    if not await check_ollama_health():
        return {
            "answer":"Ollama indisponível",
            "sources":[],
            "status":"error",
            "processing_time":
            time.time()-start_time
        }

    try:
        query_embedding = await get_embeddings(
            [req.query]
        )

        results=collection.query(
            query_embeddings=query_embedding,
            n_results=min(
                req.top_k,
                6
            ),
            include=[
                "documents",
                "metadatas"
            ]
        )

        docs=results.get(
            "documents",
            [[]]
        )[0]

        metas=results.get(
            "metadatas",
            [[]]
        )[0]

        if not docs:
            return {
                "answer":
                "Nenhum dado indexado. Execute sync.",
                "sources":[],
                "status":"no_data",
                "processing_time":
                time.time()-start_time
            }

        context="\n".join(
            [
                f"[{i+1}] "
                f"[{m.get('module').upper()} "
                f"ID:{m.get('record_id')}] "
                f"{d}"
                for i,(d,m)
                in enumerate(
                    zip(
                        docs,
                        metas
                    )
                )
            ]
        )

        prompt=f"""
            Você é um assistente especialista da Farmácia.
            Contexto:
            {context}
            
            Pergunta:
            {req.query}

            Regras:
            - Use apenas o contexto
            - Se não souber, avise
            - Cite IDs quando necessário

            Resposta:
            """

        response=await generate(
            prompt
        )

        cited_ids=list(set(re.findall(r"ID[:\s]*([A-Za-z0-9_]+)",response)))

        valid_ids=[
            f"{m.get('module')}_{m.get('record_id')}" for m in metas if m.get("record_id") in cited_ids
        ]

        return {
            "answer":response,
            "sources": valid_ids if valid_ids else [f"{m.get('module')}_{m.get('record_id')}" for m in metas[:3]],
            "status":"success",
            "processing_time":
            time.time()-start_time
        }

    except Exception as exc:
        logger.exception(
            "Erro interno ao processar chat: %s",
            exc,
        )
        return {
            "answer":
            "Erro interno",
            "sources":[],
            "status":"error",
            "processing_time":
            time.time()-start_time
        }