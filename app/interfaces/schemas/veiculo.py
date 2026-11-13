from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.enums.status_veiculo import StatusVeiculo


class DadosVeiculo(BaseModel):
    marca: str = Field(min_length=1, max_length=100)
    modelo: str = Field(min_length=1, max_length=100)
    ano: int = Field(ge=1886, le=datetime.now().year + 1)
    cor: str = Field(min_length=1, max_length=50)
    preco: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2,
    )

    @field_validator("marca", "modelo", "cor")
    @classmethod
    def validar_texto(cls, valor: str) -> str:
        valor = valor.strip()

        if not valor:
            raise ValueError("Este campo não pode ficar vazio.")

        return valor


class CadastroVeiculo(DadosVeiculo):
    pass


class AtualizacaoVeiculo(DadosVeiculo):
    pass


class RespostaVeiculo(BaseModel):
    id: UUID
    marca: str
    modelo: str
    ano: int
    cor: str
    preco: Decimal
    status: StatusVeiculo
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)