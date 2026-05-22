from fastapi import FastAPI

from RAG.routes.chat_routes import (
    router as chat_router
)

from RAG.routes.sync_routes import (
    router as sync_router
)

from RAG.routes.health_routes import (
    router as health_router
)

app = FastAPI(
    title="Farmácia AI Service (RAG)",
    version="1.0"
)

app.include_router(
    chat_router,
    prefix="/ai",
    tags=["Chat"]
)

app.include_router(
    sync_router,
    prefix="/ai",
    tags=["Sincronização"]
)

app.include_router(
    health_router,
    prefix="/ai",
    tags=["Health"]
)