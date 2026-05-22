from fastapi import APIRouter

from api.schemas.medicamento import (
    MedicamentoCreate
)
from api.services.medicamento_service import (
    MedicamentoService
)

router = APIRouter()

@router.post("/")
def criar(medicamento: MedicamentoCreate):
    return MedicamentoService.criar(medicamento)


@router.get("/")
def listar():
    return MedicamentoService.listar()