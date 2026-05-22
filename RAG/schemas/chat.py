from pydantic import BaseModel
from typing import List


class SourceChunk(BaseModel):
    id: str
    content: str


class ChatRequest(BaseModel):
    query:str
    top_k:int=4


class ChatResponse(BaseModel):
    answer:str
    sources:List[SourceChunk]
    status:str="success"
    processing_time:float=0.0