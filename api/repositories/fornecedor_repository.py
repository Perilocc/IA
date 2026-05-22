from api.core.database import db_connection
import sqlite3

class FornecedorRepository:

    @staticmethod
    def criar(fornecedor):
        conn = db_connection()

        try:
            conn.execute(
                """
                INSERT INTO fornecedores
                (empresa,cnpj,telefone)
                VALUES (?,?,?)
                """,
                (
                    fornecedor.empresa,
                    fornecedor.cnpj,
                    fornecedor.telefone
                )
            )
            conn.commit()

        except sqlite3.IntegrityError:
            raise

        finally:
            conn.close()

    @staticmethod
    def listar():
        conn = db_connection()

        rows = conn.execute(
            "SELECT * FROM fornecedores"
        ).fetchall()
        
        conn.close()
        return [dict(r) for r in rows]