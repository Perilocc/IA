from api.repositories.funcionario_repository import (
    FuncionarioRepository
)

class FuncionarioService:

    @staticmethod
    def criar(funcionario):
        if len(funcionario.nome) < 3:
            raise ValueError(
                "Nome muito curto"
            )

        FuncionarioRepository.criar(
            funcionario
        )

        return {
            "mensagem":
            "Funcionário cadastrado"
        }


    @staticmethod
    def listar():
        return {"funcionarios": FuncionarioRepository.listar()}