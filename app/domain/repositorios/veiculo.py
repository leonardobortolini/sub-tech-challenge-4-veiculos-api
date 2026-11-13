from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entidades.veiculo import Veiculo
from app.domain.enums.status_veiculo import StatusVeiculo


class RepositorioVeiculo(ABC):
    @abstractmethod
    def cadastrar(self, veiculo: Veiculo) -> Veiculo:
        pass

    @abstractmethod
    def consultar_por_id(self, veiculo_id: UUID) -> Veiculo | None:
        pass

    @abstractmethod
    def editar(self, veiculo: Veiculo) -> Veiculo:
        pass

    @abstractmethod
    def listar(
        self,
        status: StatusVeiculo | None = None,
    ) -> list[Veiculo]:
        pass
