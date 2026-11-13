from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.domain.enums.status_veiculo import StatusVeiculo


@dataclass
class Veiculo:
    id: UUID
    marca: str
    modelo: str
    ano: int
    cor: str
    preco: Decimal
    status: StatusVeiculo
    criado_em: datetime | None = None
    atualizado_em: datetime | None = None