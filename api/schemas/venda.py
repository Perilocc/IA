from pydantic import BaseModel
from typing import Optional


class VendaCreate(BaseModel):
    medicamento_id: int
    funcionario_id: int
    quantidade: int
    valor_total: float
    data_venda: Optional[str] = None


class VendaResponse(VendaCreate):
    id: int