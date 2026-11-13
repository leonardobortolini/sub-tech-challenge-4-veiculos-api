from unittest.mock import Mock, patch
from uuid import uuid4

import httpx
import pytest

from app.domain.enums.status_pagamento import StatusPagamento
from app.infrastructure.integracoes.vendas_api import (
    ErroIntegracaoVendas,
    GatewayVendasHTTP,
)


def test_notificar_pagamento_com_sucesso():
    pagamento_id = uuid4()
    resposta_mock = Mock(status_code=200)

    with patch(
        "app.infrastructure.integracoes.vendas_api.httpx.post",
        return_value=resposta_mock,
    ) as post_mock:
        gateway = GatewayVendasHTTP("http://localhost:8001")

        gateway.notificar_pagamento(
            pagamento_id,
            StatusPagamento.APROVADO,
        )

    post_mock.assert_called_once_with(
        "http://localhost:8001/compras/webhook/pagamento",
        json={
            "pagamento_id": str(pagamento_id),
            "status": "APROVADO",
        },
        timeout=10.0,
    )


def test_notificar_pagamento_com_erro_http():
    resposta_mock = Mock(status_code=500)

    with patch(
        "app.infrastructure.integracoes.vendas_api.httpx.post",
        return_value=resposta_mock,
    ):
        gateway = GatewayVendasHTTP("http://localhost:8001")

        with pytest.raises(ErroIntegracaoVendas) as erro:
            gateway.notificar_pagamento(
                uuid4(),
                StatusPagamento.APROVADO,
            )

    assert "HTTP 500" in str(erro.value)


def test_notificar_pagamento_com_falha_de_conexao():
    with patch(
        "app.infrastructure.integracoes.vendas_api.httpx.post",
        side_effect=httpx.ConnectError("Connection refused"),
    ):
        gateway = GatewayVendasHTTP("http://localhost:8001")

        with pytest.raises(ErroIntegracaoVendas) as erro:
            gateway.notificar_pagamento(
                uuid4(),
                StatusPagamento.CANCELADO,
            )

    assert "Não foi possível conectar" in str(erro.value)
