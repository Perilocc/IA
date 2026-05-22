from api.core.database import db_connection

class VendaRepository:

    @staticmethod
    def criar(venda):
        conn = db_connection()
        conn.execute(
            """
            INSERT INTO vendas
            (
                medicamento_id,
                funcionario_id,
                quantidade,
                valor_total,
                data_venda
            )
            VALUES (?,?,?,?,?)
            """,
            (
                venda.medicamento_id,
                venda.funcionario_id,
                venda.quantidade,
                venda.valor_total,
                venda.data_venda
            )
        )
        conn.commit()
        conn.close()

    @staticmethod
    def listar():
        conn = db_connection()

        rows = conn.execute(
            """
            SELECT
                v.*,
                m.nome AS medicamento,
                f.nome AS funcionario

            FROM vendas v

            LEFT JOIN medicamentos m
            ON m.id = v.medicamento_id

            LEFT JOIN funcionarios f
            ON f.id = v.funcionario_id
            """
        ).fetchall()

        conn.close()
        return [dict(r) for r in rows]