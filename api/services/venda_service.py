from api.repositories.venda_repository import (
    VendaRepository
)

class VendaService:

    @staticmethod
    def criar(venda):
        
        if venda.quantidade <= 0:

            raise ValueError(
                "Quantidade inválida"
            )

        VendaRepository.criar(
            venda
        )

        return {
            "mensagem":
            "Venda registrada"
        }


    @staticmethod
    def listar():
        return {"vendas": VendaRepository.listar()}