from fastapi import APIRouter

from RAG.schemas.sync_schema import (
    SyncStatus
)

from RAG.services.sync_service import (
    sync_index
)

router=APIRouter()

@router.post("/sync", response_model=SyncStatus)
async def sync():
    return await sync_index()