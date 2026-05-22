from api.core.database import db_connection

class MedicamentoRepository:

    @staticmethod
    def criar(medicamento):
        conn = db_connection()

        conn.execute(
            """
            INSERT INTO medicamentos
            (nome,categoria,preco,estoque,validade)
            VALUES (?,?,?,?,?)
            """,
            (
                medicamento.nome,
                medicamento.categoria,
                medicamento.preco,
                medicamento.estoque,
                medicamento.validade
            )
        )

        conn.commit()
        conn.close()

    @staticmethod
    def listar():
        conn = db_connection()

        rows = conn.execute(
            "SELECT * FROM medicamentos"
        ).fetchall()

        conn.close()
        return [dict(r) for r in rows]