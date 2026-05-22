from fastapi import APIRouter

from api.schemas.venda import (
    VendaCreate
)

from api.services.venda_service import (
    VendaService
)

router = APIRouter()

@router.post("/")
def criar(venda: VendaCreate):
    return VendaService.criar(venda)


@router.get("/")
def listar():
    return VendaService.listar()