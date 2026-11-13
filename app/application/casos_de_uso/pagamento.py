
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError

from app.domain.entidades.pagamento import Pagamento
from app.domain.enums.status_pagamento import StatusPagamento
from app.domain.enums.status_veiculo import StatusVeiculo
from app.domain.repositorios.pagamento import RepositorioPagamento
from app.domain.repositorios.veiculo import RepositorioVeiculo


class VeiculoNaoEncontrado(Exception):
    pass


class VeiculoIndisponivel(Exception):
    pass


class PagamentoNaoEncontrado(Exception):
    pass


class PagamentoPendenteExistente(Exception):
    pass


class TransicaoPagamentoInvalida(Exception):
    pass


class SolicitarPagamento:

    def __init__(
        self,
        repositorio_pagamento: RepositorioPagamento,
        repositorio_veiculo: RepositorioVeiculo,
    ):
        self.repositorio_pagamento = repositorio_pagamento
        self.repositorio_veiculo = repositorio_veiculo

    def executar(
        self,
        veiculo_id: UUID,
        cpf: str,
    ) -> Pagamento:

        veiculo = self.repositorio_veiculo.consultar_por_id(
            veiculo_id
        )

        if veiculo is None:
            raise VeiculoNaoEncontrado()

        if veiculo.status != StatusVeiculo.DISPONIVEL:
            raise VeiculoIndisponivel()

        pagamento_existente = (
            self.repositorio_pagamento.consultar_pendente_por_veiculo(
                veiculo_id
            )
        )

        if pagamento_existente is not None:
            raise PagamentoPendenteExistente()

        pagamento = Pagamento(
            id=uuid4(),
            veiculo_id=veiculo.id,
            cpf=cpf,
            valor=veiculo.preco,
            status=StatusPagamento.PENDENTE,
        )

        # Reserva o veículo antes de registrar o pagamento.
        veiculo.status = StatusVeiculo.RESERVADO
        self.repositorio_veiculo.editar(veiculo)

        try:
            return self.repositorio_pagamento.cadastrar(pagamento)

        except IntegrityError as erro:
            # O índice único parcial protege contra solicitações
            # concorrentes de pagamento para o mesmo veículo.
            veiculo.status = StatusVeiculo.DISPONIVEL
            self.repositorio_veiculo.editar(veiculo)

            raise PagamentoPendenteExistente() from erro

        except Exception:
            # Compensa a reserva caso não seja possível registrar
            # o pagamento.
            veiculo.status = StatusVeiculo.DISPONIVEL
            self.repositorio_veiculo.editar(veiculo)
            raise


class ConsultarPagamento:

    def __init__(
        self,
        repositorio_pagamento: RepositorioPagamento,
    ):
        self.repositorio_pagamento = repositorio_pagamento

    def executar(self, pagamento_id: UUID) -> Pagamento:

        pagamento = self.repositorio_pagamento.consultar_por_id(
            pagamento_id
        )

        if pagamento is None:
            raise PagamentoNaoEncontrado()

        return pagamento


class ProcessarWebhookPagamento:

    def __init__(
        self,
        repositorio_pagamento: RepositorioPagamento,
        repositorio_veiculo: RepositorioVeiculo,
    ):
        self.repositorio_pagamento = repositorio_pagamento
        self.repositorio_veiculo = repositorio_veiculo

    def executar(
        self,
        pagamento_id: UUID,
        novo_status: StatusPagamento,
    ) -> Pagamento:

        if novo_status == StatusPagamento.PENDENTE:
            raise TransicaoPagamentoInvalida(
                "O webhook não pode definir o pagamento como pendente."
            )

        pagamento = self.repositorio_pagamento.consultar_por_id(
            pagamento_id
        )

        if pagamento is None:
            raise PagamentoNaoEncontrado(
                "Pagamento não encontrado."
            )

        # Evita efeitos duplicados ao receber a mesma notificação.
        if pagamento.status == novo_status:
            return pagamento

        if pagamento.status != StatusPagamento.PENDENTE:
            raise TransicaoPagamentoInvalida(
                "Não é possível alterar um pagamento já finalizado."
            )

        veiculo = self.repositorio_veiculo.consultar_por_id(
            pagamento.veiculo_id
        )

        if veiculo is None:
            raise VeiculoNaoEncontrado(
                "Veículo não encontrado."
            )

        if veiculo.status != StatusVeiculo.RESERVADO:
            raise TransicaoPagamentoInvalida(
                "O veículo não está reservado para este pagamento."
            )

        pagamento.status = novo_status

        if novo_status == StatusPagamento.APROVADO:
            veiculo.status = StatusVeiculo.VENDIDO
        else:
            veiculo.status = StatusVeiculo.DISPONIVEL

        self.repositorio_veiculo.editar(veiculo)

        return self.repositorio_pagamento.editar(pagamento)
