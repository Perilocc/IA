from pydantic import BaseModel
from typing import Optional


class DocumentUploadStatus(BaseModel):
    status: str
    indexed: int
    files: int
    message: str
    last_sync: Optional[str] = None