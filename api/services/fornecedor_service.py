from fastapi import HTTPException
import sqlite3

from api.repositories.fornecedor_repository import (
    FornecedorRepository
)


class FornecedorService:

    @staticmethod
    def criar(fornecedor):
        try:
            FornecedorRepository.criar(
                fornecedor
            )

            return {
                "mensagem":
                "Fornecedor cadastrado"
            }

        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=400,
                detail="CNPJ já cadastrado"
            )


    @staticmethod
    def listar():
        return {"fornecedores": FornecedorRepository.listar()}