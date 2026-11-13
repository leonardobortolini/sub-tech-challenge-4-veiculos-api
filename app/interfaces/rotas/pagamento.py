from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

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
from app.domain.enums.status_pagamento import StatusPagamento
from app.infrastructure.database import get_db
from app.infrastructure.repositorios.pagamento import (
    RepositorioPagamentoSQLAlchemy,
)
from app.infrastructure.repositorios.veiculo import (
    RepositorioVeiculoSQLAlchemy,
)
from app.interfaces.schemas.pagamento import (
    RespostaPagamento,
    SolicitacaoPagamento,
    WebhookPagamento,
)
from app.infrastructure.config import configuracoes
from app.infrastructure.integracoes.vendas_api import (
    ErroIntegracaoVendas,
    GatewayVendasHTTP,
)


pagamentos_router = APIRouter(
    prefix="/pagamentos",
    tags=["Pagamentos"],
)


@pagamentos_router.post(
    "",
    response_model=RespostaPagamento,
    status_code=status.HTTP_201_CREATED,
    summary="Solicitar pagamento",
    description="Cria uma solicitação de pagamento para um veículo disponível.",
)
def solicitar_pagamento(
    dados: SolicitacaoPagamento,
    banco: Session = Depends(get_db),
):
    repositorio_pagamento = RepositorioPagamentoSQLAlchemy(banco)
    repositorio_veiculo = RepositorioVeiculoSQLAlchemy(banco)

    caso_de_uso = SolicitarPagamento(
        repositorio_pagamento,
        repositorio_veiculo,
    )

    try:
        return caso_de_uso.executar(
            veiculo_id=dados.veiculo_id,
            cpf=dados.cpf,
        )

    except VeiculoNaoEncontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado.",
        )

    except (VeiculoIndisponivel, PagamentoPendenteExistente):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Veículo indisponível para pagamento.",
        )


@pagamentos_router.get(
    "/{pagamento_id}",
    response_model=RespostaPagamento,
    summary="Consultar pagamento",
    description="Consulta um pagamento pelo seu identificador.",
)
def consultar_pagamento(
    pagamento_id: UUID,
    banco: Session = Depends(get_db),
):
    repositorio_pagamento = RepositorioPagamentoSQLAlchemy(banco)

    caso_de_uso = ConsultarPagamento(repositorio_pagamento)

    try:
        return caso_de_uso.executar(pagamento_id)

    except PagamentoNaoEncontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pagamento não encontrado.",
        )


@pagamentos_router.post(
    "/webhook",
    response_model=RespostaPagamento,
    summary="Receber notificação de pagamento",
    description=(
        "Recebe a confirmação ou o cancelamento de um pagamento "
        "e atualiza o status do veículo."
    ),
)
def processar_webhook_pagamento(
    dados: WebhookPagamento,
    banco: Session = Depends(get_db),
):
    repositorio_pagamento = RepositorioPagamentoSQLAlchemy(banco)
    repositorio_veiculo = RepositorioVeiculoSQLAlchemy(banco)

    caso_de_uso = ProcessarWebhookPagamento(
        repositorio_pagamento,
        repositorio_veiculo,
    )

    try:
        pagamento = caso_de_uso.executar(
            pagamento_id=dados.pagamento_id,
            novo_status=StatusPagamento(dados.status),
        )

        gateway_vendas = GatewayVendasHTTP(configuracoes.vendas_api_url)

        gateway_vendas.notificar_pagamento(
            pagamento_id=pagamento.id,
            status=pagamento.status,
        )

        return pagamento

    except PagamentoNaoEncontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pagamento não encontrado.",
        )

    except (VeiculoNaoEncontrado, TransicaoPagamentoInvalida) as erro:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(erro),
        )

    except ErroIntegracaoVendas as erro:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Pagamento processado, mas não foi possível "
                "notificar a API de vendas. Reenvie o webhook. "
                f"Detalhe: {erro}"
            ),
        ) from erro
