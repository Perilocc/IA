from api.core.database import db_connection

class DashboardRepository:
    
    @staticmethod
    def obter_dados():
        conn = db_connection()

        total_medicamentos = conn.execute(
            "SELECT COUNT(*) FROM medicamentos"
        ).fetchone()[0]

        estoque_baixo = conn.execute(
            """
            SELECT COUNT(*)
            FROM medicamentos
            WHERE estoque < 10
            """
        ).fetchone()[0]

        total_funcionarios = conn.execute(
            "SELECT COUNT(*) FROM funcionarios"
        ).fetchone()[0]

        total_vendas = conn.execute(
            "SELECT COUNT(*) FROM vendas"
        ).fetchone()[0]

        conn.close()

        return {
            "medicamentos": {
                "total": total_medicamentos,
                "estoque_baixo": estoque_baixo
            },
            "funcionarios": {
                "total": total_funcionarios
            },
            "vendas": {
                "total": total_vendas
            }
        }