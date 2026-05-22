from pydantic import BaseModel
from typing import Optional


class FornecedorCreate(BaseModel):
    empresa: str
    cnpj: str
    telefone: Optional[str] = None


class FornecedorResponse(FornecedorCreate):
    id: int
    criado_em: str