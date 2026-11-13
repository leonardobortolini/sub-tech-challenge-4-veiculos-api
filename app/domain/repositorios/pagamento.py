from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entidades.pagamento import Pagamento


class RepositorioPagamento(ABC):

    @abstractmethod
    def cadastrar(self, pagamento: Pagamento) -> Pagamento:
        pass

    @abstractmethod
    def consultar_por_id(self, pagamento_id: UUID) -> Pagamento | None:
        pass

    @abstractmethod
    def consultar_por_veiculo(
        self,
        veiculo_id: UUID,
    ) -> list[Pagamento]:
        pass

    @abstractmethod
    def consultar_pendente_por_veiculo(
        self,
        veiculo_id: UUID,
    ) -> Pagamento | None:
        pass

    @abstractmethod
    def editar(self, pagamento: Pagamento) -> Pagamento:
        pass