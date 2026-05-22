from api.repositories.dashboard_repository import (
    DashboardRepository
)

class DashboardService:

    @staticmethod
    def obter():
        return (DashboardRepository.obter_dados())