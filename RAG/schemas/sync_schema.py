from pydantic import BaseModel
from typing import Optional


class SyncStatus(BaseModel):
    status:str
    indexed:int
    message:str
    last_sync:Optional[str]=None