import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class ModeloVeiculo(Base):
    __tablename__ = "veiculos"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    marca: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    modelo: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    ano: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    cor: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    preco: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="DISPONIVEL",
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )