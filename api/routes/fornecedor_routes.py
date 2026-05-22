from fastapi import APIRouter

from api.schemas.fornecedor import (
    FornecedorCreate
)

from api.services.fornecedor_service import (
    FornecedorService
)

router = APIRouter()

@router.post("/")
def criar(fornecedor: FornecedorCreate):
    return FornecedorService.criar(fornecedor)

@router.get("/")
def listar():
    return FornecedorService.listar()