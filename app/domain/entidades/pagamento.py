from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.domain.enums.status_pagamento import StatusPagamento


@dataclass
class Pagamento:
    id: UUID
    veiculo_id: UUID
    cpf: str
    valor: Decimal
    status: StatusPagamento
    criado_em: datetime | None = None
    atualizado_em: datetime | None = None