from api.core.database import db_connection

class FuncionarioRepository:

    @staticmethod
    def criar(funcionario):
        conn = db_connection()
        conn.execute(
            """
            INSERT INTO funcionarios
            (nome,cargo,telefone,status)
            VALUES (?,?,?,?)
            """,
            (
                funcionario.nome,
                funcionario.cargo,
                funcionario.telefone,
                funcionario.status
            )
        )

        conn.commit()
        conn.close()

    @staticmethod
    def listar():
        conn = db_connection()

        rows = conn.execute(
            "SELECT * FROM funcionarios"
        ).fetchall()

        conn.close()
        return [dict(r) for r in rows]