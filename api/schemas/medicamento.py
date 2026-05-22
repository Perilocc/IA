from pydantic import BaseModel
from typing import Optional


class MedicamentoCreate(BaseModel):
    nome: str
    categoria: str
    preco: float
    estoque: int
    validade: Optional[str] = None


class MedicamentoResponse(MedicamentoCreate):
    id: int
    criado_em: str