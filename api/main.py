from contextlib import asynccontextmanager
from api.core.database import create_tables
from fastapi import FastAPI

from api.routes.medicamento_routes import (
    router as medicamento_router
)

from api.routes.funcionario_routes import (
    router as funcionario_router
)

from api.routes.fornecedor_routes import (
    router as fornecedor_router
)

from api.routes.venda_routes import (
    router as venda_router
)

from api.routes.dashboard_routes import (
    router as dashboard_router
)

app = FastAPI(title="API Farmácia", version="2.0")

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app.include_router(
    medicamento_router,
    prefix="/medicamentos",
    tags=["Medicamentos"]
)

app.include_router(
    funcionario_router,
    prefix="/funcionarios",
    tags=["Funcionários"]
)

app.include_router(
    fornecedor_router,
    prefix="/fornecedores",
    tags=["Fornecedores"]
)

app.include_router(
    venda_router,
    prefix="/vendas",
    tags=["Vendas"]
)

app.include_router(
    dashboard_router,
    prefix="/dashboard",
    tags=["Dashboard"]
)