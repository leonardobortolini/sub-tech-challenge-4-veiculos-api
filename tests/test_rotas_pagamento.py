from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.application.casos_de_uso.pagamento import (
    PagamentoNaoEncontrado,
    TransicaoPagamentoInvalida,
)
from app.domain.enums.status_pagamento import StatusPagamento
from app.infrastructure.database import get_db
from app.infrastructure.integracoes.vendas_api import (
    ErroIntegracaoVendas,
)
from app.main import app


cliente = TestClient(app)


def criar_pagamento(status=StatusPagamento.APROVADO):
    return SimpleNamespace(
        id=uuid4(),
        veiculo_id=uuid4(),
        cpf="12345678901",
        valor=Decimal("135000.00"),
        status=status,
        criado_em=datetime.now(),
        atualizado_em=datetime.now(),
    )


def configurar_dependencia_banco():
    app.dependency_overrides[get_db] = lambda: Mock()


def limpar_dependencias():
    app.dependency_overrides.clear()


def test_webhook_aprovar_pagamento_notifica_vendas(monkeypatch):
    pagamento = criar_pagamento()

    configurar_dependencia_banco()

    caso_uso_mock = Mock()
    caso_uso_mock.executar.return_value = pagamento

    gateway_mock = Mock()

    monkeypatch.setattr(
        "app.interfaces.rotas.pagamento.ProcessarWebhookPagamento",
        lambda *args: caso_uso_mock,
    )

    monkeypatch.setattr(
        "app.interfaces.rotas.pagamento.GatewayVendasHTTP",
        lambda *args: gateway_mock,
    )

    try:
        resposta = cliente.post(
            "/pagamentos/webhook",
            json={
                "pagamento_id": str(pagamento.id),
                "status": "APROVADO",
            },
        )
    finally:
        limpar_dependencias()

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "APROVADO"

    gateway_mock.notificar_pagamento.assert_called_once_with(
        pagamento_id=pagamento.id,
        status=StatusPagamento.APROVADO,
    )


def test_webhook_cancelar_pagamento_notifica_vendas(monkeypatch):
    pagamento = criar_pagamento(StatusPagamento.CANCELADO)

    configurar_dependencia_banco()

    caso_uso_mock = Mock()
    caso_uso_mock.executar.return_value = pagamento

    gateway_mock = Mock()

    monkeypatch.setattr(
        "app.interfaces.rotas.pagamento.ProcessarWebhookPagamento",
        lambda *args: caso_uso_mock,
    )

    monkeypatch.setattr(
        "app.interfaces.rotas.pagamento.GatewayVendasHTTP",
        lambda *args: gateway_mock,
    )

    try:
        resposta = cliente.post(
            "/pagamentos/webhook",
            json={
                "pagamento_id": str(pagamento.id),
                "status": "CANCELADO",
            },
        )
    finally:
        limpar_dependencias()

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "CANCELADO"

    gateway_mock.notificar_pagamento.assert_called_once_with(
        pagamento_id=pagamento.id,
        status=StatusPagamento.CANCELADO,
    )


def test_webhook_retorna_502_quando_integracao_falha(monkeypatch):
    pagamento = criar_pagamento()

    configurar_dependencia_banco()

    caso_uso_mock = Mock()
    caso_uso_mock.executar.return_value = pagamento

    gateway_mock = Mock()
    gateway_mock.notificar_pagamento.side_effect = ErroIntegracaoVendas(
        "API de vendas indisponível."
    )

    monkeypatch.setattr(
        "app.interfaces.rotas.pagamento.ProcessarWebhookPagamento",
        lambda *args: caso_uso_mock,
    )

    monkeypatch.setattr(
        "app.interfaces.rotas.pagamento.GatewayVendasHTTP",
        lambda *args: gateway_mock,
    )

    try:
        resposta = cliente.post(
            "/pagamentos/webhook",
            json={
                "pagamento_id": str(pagamento.id),
                "status": "APROVADO",
            },
        )
    finally:
        limpar_dependencias()

    assert resposta.status_code == 502
    assert "Pagamento processado" in resposta.json()["detail"]
    assert "Reenvie o webhook" in resposta.json()["detail"]

    caso_uso_mock.executar.assert_called_once()


def test_webhook_retorna_404_quando_pagamento_nao_existe(monkeypatch):
    configurar_dependencia_banco()

    caso_uso_mock = Mock()
    caso_uso_mock.executar.side_effect = PagamentoNaoEncontrado()

    gateway_mock = Mock()

    monkeypatch.setattr(
        "app.interfaces.rotas.pagamento.ProcessarWebhookPagamento",
        lambda *args: caso_uso_mock,
    )

    monkeypatch.setattr(
        "app.interfaces.rotas.pagamento.GatewayVendasHTTP",
        lambda *args: gateway_mock,
    )

    try:
        resposta = cliente.post(
            "/pagamentos/webhook",
            json={
                "pagamento_id": str(uuid4()),
                "status": "APROVADO",
            },
        )
    finally:
        limpar_dependencias()

    assert resposta.status_code == 404

    gateway_mock.notificar_pagamento.assert_not_called()


def test_webhook_retorna_409_quando_transicao_e_invalida(monkeypatch):
    configurar_dependencia_banco()

    caso_uso_mock = Mock()
    caso_uso_mock.executar.side_effect = TransicaoPagamentoInvalida(
        "Transição de pagamento inválida."
    )

    gateway_mock = Mock()

    monkeypatch.setattr(
        "app.interfaces.rotas.pagamento.ProcessarWebhookPagamento",
        lambda *args: caso_uso_mock,
    )

    monkeypatch.setattr(
        "app.interfaces.rotas.pagamento.GatewayVendasHTTP",
        lambda *args: gateway_mock,
    )

    try:
        resposta = cliente.post(
            "/pagamentos/webhook",
            json={
                "pagamento_id": str(uuid4()),
                "status": "APROVADO",
            },
        )
    finally:
        limpar_dependencias()

    assert resposta.status_code == 409

    gateway_mock.notificar_pagamento.assert_not_called()
