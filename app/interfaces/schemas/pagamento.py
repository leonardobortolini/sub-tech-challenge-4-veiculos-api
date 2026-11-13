
from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums.status_pagamento import StatusPagamento


class SolicitacaoPagamento(BaseModel):
    veiculo_id: UUID
    cpf: str = Field(
        min_length=11,
        max_length=11,
        pattern=r"^\d{11}$",
        description="CPF do comprador, contendo 11 dígitos",
    )


class RespostaPagamento(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    veiculo_id: UUID
    cpf: str
    valor: Decimal
    status: StatusPagamento
    criado_em: datetime | None = None
    atualizado_em: datetime | None = None


class WebhookPagamento(BaseModel):
    pagamento_id: UUID
    status: Literal["APROVADO", "CANCELADO"]
