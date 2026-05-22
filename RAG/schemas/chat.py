from pydantic import BaseModel
from typing import List


class ChatRequest(BaseModel):
    query:str
    top_k:int=4


class ChatResponse(BaseModel):
    answer:str
    sources:List[str]
    status:str="success"
    processing_time:float=0.0