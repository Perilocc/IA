from fastapi import APIRouter

from api.services.dashboard_service import (
    DashboardService
)

router = APIRouter()

@router.get("/")
def dashboard():
    return DashboardService.obter()