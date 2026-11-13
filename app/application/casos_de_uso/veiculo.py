from decimal import Decimal
from uuid import UUID, uuid4

from app.domain.entidades.veiculo import Veiculo
from app.domain.enums.status_veiculo import StatusVeiculo
from app.domain.repositorios.veiculo import RepositorioVeiculo


class VeiculoNaoEncontrado(Exception):
    pass


class VeiculoNaoPodeSerEditado(Exception):
    pass


class CadastrarVeiculo:
    def __init__(self, repositorio: RepositorioVeiculo):
        self.repositorio = repositorio

    def executar(
        self,
        marca: str,
        modelo: str,
        ano: int,
        cor: str,
        preco: Decimal,
    ) -> Veiculo:
        veiculo = Veiculo(
            id=uuid4(),
            marca=marca,
            modelo=modelo,
            ano=ano,
            cor=cor,
            preco=preco,
            status=StatusVeiculo.DISPONIVEL,
        )

        return self.repositorio.cadastrar(veiculo)


class ConsultarVeiculo:
    def __init__(self, repositorio: RepositorioVeiculo):
        self.repositorio = repositorio

    def executar(self, veiculo_id: UUID) -> Veiculo:
        veiculo = self.repositorio.consultar_por_id(veiculo_id)

        if veiculo is None:
            raise VeiculoNaoEncontrado("Veículo não encontrado.")

        return veiculo


class EditarVeiculo:
    def __init__(self, repositorio: RepositorioVeiculo):
        self.repositorio = repositorio

    def executar(
        self,
        veiculo_id: UUID,
        marca: str,
        modelo: str,
        ano: int,
        cor: str,
        preco: Decimal,
    ) -> Veiculo:
        veiculo = self.repositorio.consultar_por_id(veiculo_id)

        if veiculo is None:
            raise VeiculoNaoEncontrado("Veículo não encontrado.")

        if veiculo.status != StatusVeiculo.DISPONIVEL:
            raise VeiculoNaoPodeSerEditado(
                "Somente veículos disponíveis podem ser editados."
            )

        veiculo.marca = marca
        veiculo.modelo = modelo
        veiculo.ano = ano
        veiculo.cor = cor
        veiculo.preco = preco

        return self.repositorio.editar(veiculo)


class ListarVeiculos:
    def __init__(self, repositorio: RepositorioVeiculo):
        self.repositorio = repositorio

    def executar(
        self,
        status: StatusVeiculo | None = None,
    ) -> list[Veiculo]:
        return self.repositorio.listar(status)
