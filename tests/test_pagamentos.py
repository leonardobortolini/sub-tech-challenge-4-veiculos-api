
from decimal import Decimal
from uuid import uuid4

import pytest

from app.application.casos_de_uso.pagamento import (
    ConsultarPagamento,
    PagamentoNaoEncontrado,
    PagamentoPendenteExistente,
    ProcessarWebhookPagamento,
    SolicitarPagamento,
    TransicaoPagamentoInvalida,
    VeiculoIndisponivel,
    VeiculoNaoEncontrado,
)
from app.domain.entidades.pagamento import Pagamento
from app.domain.entidades.veiculo import Veiculo
from app.domain.enums.status_pagamento import StatusPagamento
from app.domain.enums.status_veiculo import StatusVeiculo


class RepositorioVeiculoFake:

    def __init__(self, veiculo=None):
        self.veiculo = veiculo
        self.quantidade_edicoes = 0

    def consultar_por_id(self, veiculo_id):
        if self.veiculo and self.veiculo.id == veiculo_id:
            return self.veiculo
        return None

    def editar(self, veiculo):
        self.veiculo = veiculo
        self.quantidade_edicoes += 1
        return veiculo


class RepositorioPagamentoFake:

    def __init__(self, pagamento_pendente=None, pagamento=None):
        self.pagamento_pendente = pagamento_pendente
        self.pagamento = pagamento
        self.pagamentos = []
        self.quantidade_edicoes = 0

    def consultar_pendente_por_veiculo(self, veiculo_id):
        return self.pagamento_pendente

    def cadastrar(self, pagamento):
        self.pagamentos.append(pagamento)
        self.pagamento = pagamento
        return pagamento

    def editar(self, pagamento):
        self.pagamento = pagamento
        self.quantidade_edicoes += 1
        return pagamento

    def consultar_por_id(self, pagamento_id):
        if self.pagamento and self.pagamento.id == pagamento_id:
            return self.pagamento
        return None


@pytest.fixture
def veiculo():
    return Veiculo(
        id=uuid4(),
        marca="Toyota",
        modelo="Corolla",
        ano=2024,
        cor="Prata",
        preco=Decimal("135000.00"),
        status=StatusVeiculo.DISPONIVEL,
    )


@pytest.fixture
def pagamento(veiculo):
    return Pagamento(
        id=uuid4(),
        veiculo_id=veiculo.id,
        cpf="12345678901",
        valor=Decimal("135000.00"),
        status=StatusPagamento.PENDENTE,
    )


def test_solicitar_pagamento_com_sucesso(veiculo):
    repositorio_veiculo = RepositorioVeiculoFake(veiculo)
    repositorio_pagamento = RepositorioPagamentoFake()

    caso_de_uso = SolicitarPagamento(
        repositorio_pagamento,
        repositorio_veiculo,
    )

    pagamento = caso_de_uso.executar(
        veiculo.id,
        "12345678901",
    )

    assert pagamento.status == StatusPagamento.PENDENTE
    assert pagamento.veiculo_id == veiculo.id
    assert pagamento.cpf == "12345678901"
    assert pagamento.valor == Decimal("135000.00")
    assert veiculo.status == StatusVeiculo.RESERVADO


def test_nao_solicitar_pagamento_para_veiculo_inexistente():
    repositorio_veiculo = RepositorioVeiculoFake()
    repositorio_pagamento = RepositorioPagamentoFake()

    caso_de_uso = SolicitarPagamento(
        repositorio_pagamento,
        repositorio_veiculo,
    )

    with pytest.raises(VeiculoNaoEncontrado):
        caso_de_uso.executar(uuid4(), "12345678901")


def test_nao_solicitar_pagamento_para_veiculo_indisponivel(veiculo):
    veiculo.status = StatusVeiculo.VENDIDO

    caso_de_uso = SolicitarPagamento(
        RepositorioPagamentoFake(),
        RepositorioVeiculoFake(veiculo),
    )

    with pytest.raises(VeiculoIndisponivel):
        caso_de_uso.executar(veiculo.id, "12345678901")


def test_nao_solicitar_pagamento_com_outro_pendente(veiculo):
    pagamento_existente = Pagamento(
        id=uuid4(),
        veiculo_id=veiculo.id,
        cpf="12345678901",
        valor=Decimal("135000.00"),
        status=StatusPagamento.PENDENTE,
    )

    caso_de_uso = SolicitarPagamento(
        RepositorioPagamentoFake(
            pagamento_pendente=pagamento_existente
        ),
        RepositorioVeiculoFake(veiculo),
    )

    with pytest.raises(PagamentoPendenteExistente):
        caso_de_uso.executar(veiculo.id, "98765432100")


def test_consultar_pagamento_com_sucesso():
    pagamento = Pagamento(
        id=uuid4(),
        veiculo_id=uuid4(),
        cpf="12345678901",
        valor=Decimal("135000.00"),
        status=StatusPagamento.PENDENTE,
    )

    caso_de_uso = ConsultarPagamento(
        RepositorioPagamentoFake(pagamento=pagamento)
    )

    resultado = caso_de_uso.executar(pagamento.id)

    assert resultado.id == pagamento.id
    assert resultado.status == StatusPagamento.PENDENTE


def test_consultar_pagamento_inexistente():
    caso_de_uso = ConsultarPagamento(
        RepositorioPagamentoFake()
    )

    with pytest.raises(PagamentoNaoEncontrado):
        caso_de_uso.executar(uuid4())


# Testes do webhook


def test_webhook_aprovar_pagamento_com_sucesso(veiculo, pagamento):
    veiculo.status = StatusVeiculo.RESERVADO

    repositorio_veiculo = RepositorioVeiculoFake(veiculo)
    repositorio_pagamento = RepositorioPagamentoFake(
        pagamento=pagamento
    )

    caso_de_uso = ProcessarWebhookPagamento(
        repositorio_pagamento,
        repositorio_veiculo,
    )

    resultado = caso_de_uso.executar(
        pagamento.id,
        StatusPagamento.APROVADO,
    )

    assert resultado.status == StatusPagamento.APROVADO
    assert veiculo.status == StatusVeiculo.VENDIDO


def test_webhook_cancelar_pagamento_com_sucesso(veiculo, pagamento):
    veiculo.status = StatusVeiculo.RESERVADO

    repositorio_veiculo = RepositorioVeiculoFake(veiculo)
    repositorio_pagamento = RepositorioPagamentoFake(
        pagamento=pagamento
    )

    caso_de_uso = ProcessarWebhookPagamento(
        repositorio_pagamento,
        repositorio_veiculo,
    )

    resultado = caso_de_uso.executar(
        pagamento.id,
        StatusPagamento.CANCELADO,
    )

    assert resultado.status == StatusPagamento.CANCELADO
    assert veiculo.status == StatusVeiculo.DISPONIVEL


def test_webhook_nao_deve_processar_novamente_a_mesma_notificacao(
    veiculo,
    pagamento,
):
    veiculo.status = StatusVeiculo.RESERVADO

    repositorio_veiculo = RepositorioVeiculoFake(veiculo)
    repositorio_pagamento = RepositorioPagamentoFake(
        pagamento=pagamento
    )

    caso_de_uso = ProcessarWebhookPagamento(
        repositorio_pagamento,
        repositorio_veiculo,
    )

    primeiro_resultado = caso_de_uso.executar(
        pagamento.id,
        StatusPagamento.APROVADO,
    )

    segundo_resultado = caso_de_uso.executar(
        pagamento.id,
        StatusPagamento.APROVADO,
    )

    assert primeiro_resultado.status == StatusPagamento.APROVADO
    assert segundo_resultado.status == StatusPagamento.APROVADO
    assert veiculo.status == StatusVeiculo.VENDIDO

    # A segunda notificação não deve executar novas gravações.
    assert repositorio_pagamento.quantidade_edicoes == 1
    assert repositorio_veiculo.quantidade_edicoes == 1


def test_webhook_nao_deve_cancelar_pagamento_aprovado(
    veiculo,
    pagamento,
):
    pagamento.status = StatusPagamento.APROVADO
    veiculo.status = StatusVeiculo.VENDIDO

    caso_de_uso = ProcessarWebhookPagamento(
        RepositorioPagamentoFake(pagamento=pagamento),
        RepositorioVeiculoFake(veiculo),
    )

    with pytest.raises(TransicaoPagamentoInvalida):
        caso_de_uso.executar(
            pagamento.id,
            StatusPagamento.CANCELADO,
        )


def test_webhook_nao_deve_processar_pagamento_inexistente():
    caso_de_uso = ProcessarWebhookPagamento(
        RepositorioPagamentoFake(),
        RepositorioVeiculoFake(),
    )

    with pytest.raises(PagamentoNaoEncontrado):
        caso_de_uso.executar(
            uuid4(),
            StatusPagamento.APROVADO,
        )


def test_webhook_nao_deve_processar_veiculo_nao_reservado(
    veiculo,
    pagamento,
):
    veiculo.status = StatusVeiculo.DISPONIVEL

    caso_de_uso = ProcessarWebhookPagamento(
        RepositorioPagamentoFake(pagamento=pagamento),
        RepositorioVeiculoFake(veiculo),
    )

    with pytest.raises(TransicaoPagamentoInvalida):
        caso_de_uso.executar(
            pagamento.id,
            StatusPagamento.APROVADO,
        )


def test_webhook_nao_deve_aceitar_status_pendente(
    veiculo,
    pagamento,
):
    caso_de_uso = ProcessarWebhookPagamento(
        RepositorioPagamentoFake(pagamento=pagamento),
        RepositorioVeiculoFake(veiculo),
    )

    with pytest.raises(TransicaoPagamentoInvalida):
        caso_de_uso.executar(
            pagamento.id,
            StatusPagamento.PENDENTE,
        )


def test_webhook_nao_deve_processar_pagamento_com_veiculo_inexistente(
    pagamento,
):
    caso_de_uso = ProcessarWebhookPagamento(
        RepositorioPagamentoFake(pagamento=pagamento),
        RepositorioVeiculoFake(),
    )

    with pytest.raises(VeiculoNaoEncontrado):
        caso_de_uso.executar(
            pagamento.id,
            StatusPagamento.APROVADO,
        )
