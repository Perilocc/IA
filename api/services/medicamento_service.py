from api.repositories.medicamento_repository import (
    MedicamentoRepository
)

class MedicamentoService:

    @staticmethod
    def criar(medicamento):

        if medicamento.preco <= 0:
            raise ValueError(
                "Preço deve ser maior que zero"
            )

        if medicamento.estoque < 0:
            raise ValueError(
                "Estoque inválido"
            )

        MedicamentoRepository.criar(
            medicamento
        )

        return {
            "mensagem": "Medicamento cadastrado"
        }


    @staticmethod
    def listar():
        return {"medicamentos": MedicamentoRepository.listar()}