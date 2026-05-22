from fastapi import APIRouter

from api.schemas.funcionario import (
    FuncionarioCreate
)

from api.services.funcionario_service import (
    FuncionarioService
)

router = APIRouter()

@router.post("/")
def criar(funcionario: FuncionarioCreate):
    return FuncionarioService.criar(funcionario)


@router.get("/")
def listar():
    return FuncionarioService.listar()