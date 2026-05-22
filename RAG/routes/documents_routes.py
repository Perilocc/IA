from fastapi import APIRouter, File, UploadFile

from RAG.schemas.document import DocumentUploadStatus
from RAG.services.document_service import index_uploaded_documents

router = APIRouter()


@router.post("/documents/upload", response_model=DocumentUploadStatus)
async def upload_documents(files: list[UploadFile] = File(...)):
    return await index_uploaded_documents(files)