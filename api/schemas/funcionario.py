from pydantic import BaseModel
from typing import Optional


class FuncionarioCreate(BaseModel):
    nome: str
    cargo: str
    telefone: Optional[str] = None
    status: Optional[str] = "Ativo"


class FuncionarioResponse(FuncionarioCreate):
    id: int
    criado_em: str