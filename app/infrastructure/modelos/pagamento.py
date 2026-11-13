
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums.status_pagamento import StatusPagamento
from app.infrastructure.database import Base


class ModeloPagamento(Base):
    __tablename__ = "pagamentos"

    __table_args__ = (
        Index(
            "uq_pagamentos_veiculo_pendente",
            "veiculo_id",
            unique=True,
            postgresql_where=text("status = 'PENDENTE'"),
            sqlite_where=text("status = 'PENDENTE'"),
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    veiculo_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("veiculos.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    cpf: Mapped[str] = mapped_column(
        String(11),
        nullable=False,
    )

    valor: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=StatusPagamento.PENDENTE.value,
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
