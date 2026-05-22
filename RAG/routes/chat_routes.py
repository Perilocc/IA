from fastapi import APIRouter

from RAG.schemas.chat import (
    ChatRequest,
    ChatResponse
)

from RAG.services.rag_service import (
    process_chat
)

router=APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(req:ChatRequest):
    return await process_chat(req)