from uuid import UUID

import httpx

from app.domain.enums.status_pagamento import StatusPagamento


class ErroIntegracaoVendas(Exception):
    pass


class GatewayVendasHTTP:
    def __init__(self, url_base: str):
        self.url_base = url_base.rstrip("/")

    def notificar_pagamento(
        self,
        pagamento_id: UUID,
        status: StatusPagamento,
    ) -> None:
        try:
            resposta = httpx.post(
                f"{self.url_base}/compras/webhook/pagamento",
                json={
                    "pagamento_id": str(pagamento_id),
                    "status": status.value,
                },
                timeout=10.0,
            )

        except httpx.RequestError as erro:
            raise ErroIntegracaoVendas(
                "Não foi possível conectar à API de vendas."
            ) from erro

        if resposta.status_code != 200:
            raise ErroIntegracaoVendas(
                f"A API de vendas retornou HTTP {resposta.status_code}."
            )
