from sentence_transformers import CrossEncoder
import re
import time
import asyncio

from fastapi import HTTPException

from RAG.core.chroma import collection
from RAG.core.logging_config import logger

from RAG.services.ollama_service import (
    get_embeddings,
    generate,
    check_ollama_health
)

ranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def expand_query(query: str):
    return [
        query,
        f"Explique detalhadamente: {query}",
        f"Contexto técnico sobre {query}",
    ]

def rerank(query, docs, metas, top_k):
    if not docs:
        return [], []

    pairs = [[query, d] for d in docs]
    scores = ranker.predict(pairs)

    scored = sorted(
        zip(docs, metas, scores),
        key=lambda x: x[2],
        reverse=True
    )

    top = scored[:top_k]

    docs = [d for d, m, s in top]
    metas = [m for d, m, s in top]

    return docs, metas

async def validate_context(query, context):
    prompt = f"""
        Você é um avaliador de contexto.

        Pergunta: {query}

        Contexto:
        {context}

        Esse contexto contém informação suficiente para responder?
        Responda apenas SIM ou NÃO.
    """

    result = await generate(prompt)
    return "SIM" in result.upper()

async def process_chat(req):
    start_time = time.time()

    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query obrigatória")

    if not await check_ollama_health():
        return {
            "answer": "Ollama indisponível",
            "sources": [],
            "status": "error",
            "processing_time": time.time() - start_time
        }

    try:
        # ==========================================
        #            QUERY EXPANSION
        # ==========================================
        queries = expand_query(req.query)

        all_docs = []
        all_metas = []

        # ==========================================
        #            MULTI-RETRIEVAL
        # ==========================================
        for q in queries:
            query_embedding = await get_embeddings([q])

            results = collection.query(
                query_embeddings=query_embedding,
                n_results=min(req.top_k, 6),
                include=["documents", "metadatas"]
            )

            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]

            all_docs.extend(docs)
            all_metas.extend(metas)

        if not all_docs:
            return {
                "answer": "Nenhum dado indexado. Execute sync.",
                "sources": [],
                "status": "no_data",
                "processing_time": time.time() - start_time
            }

        unique = {}
        for d, m in zip(all_docs, all_metas):
            key = m.get("record_id")
            unique[key] = (d, m)

        docs, metas = zip(*unique.values())

        docs = list(docs)
        metas = list(metas)

        # ==========================================
        #                RE-RANKING
        # ==========================================
        docs, metas = rerank(
            req.query,
            docs,
            metas,
            req.top_k
        )

        context = "\n".join(
            [
                f"[{i+1}] [{m.get('module').upper()} "
                f"ID:{m.get('record_id')}] "
                f"{d[:300]}"
                for i, (d, m) in enumerate(zip(docs, metas))
            ]
        )

        is_valid = await validate_context(req.query, context)

        if not is_valid:
            # fallback inteligente (RAG retry simples)
            logger.warning("Contexto rejeitado pelo validador LLM")

            # estratégia simples: aumenta recall
            query_embedding = await get_embeddings([req.query])

            results = collection.query(
                query_embeddings=query_embedding,
                n_results=10,  # aumenta recall
                include=["documents", "metadatas"]
            )

            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]

            context = "\n".join(
                [
                    f"[{i+1}] [{m.get('module').upper()} "
                    f"ID:{m.get('record_id')}] "
                    f"{d[:300]}"
                    for i, (d, m) in enumerate(zip(docs, metas))
                ]
            )

        prompt = f"""
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

        response = await generate(prompt)

        cited_ids = list(set(
            re.findall(r"ID[:\s]*([A-Za-z0-9_]+)", response)
        ))

        valid_ids = [
            f"{m.get('module')}_{m.get('record_id')}"
            for m in metas
            if m.get("record_id") in cited_ids
        ]

        return {
            "answer": response,
            "sources": valid_ids if valid_ids else [
                f"{m.get('module')}_{m.get('record_id')}"
                for m in metas[:3]
            ],
            "status": "success",
            "processing_time": time.time() - start_time
        }

    except Exception as exc:
        logger.exception("Erro interno ao processar chat: %s", exc)

        return {
            "answer": "Erro interno",
            "sources": [],
            "status": "error",
            "processing_time": time.time() - start_time
        }