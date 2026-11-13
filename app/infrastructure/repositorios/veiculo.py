from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.domain.entidades.veiculo import Veiculo
from app.domain.enums.status_veiculo import StatusVeiculo
from app.domain.repositorios.veiculo import RepositorioVeiculo
from app.infrastructure.modelos.veiculo import ModeloVeiculo


class RepositorioVeiculoSQLAlchemy(RepositorioVeiculo):
    def __init__(self, banco: Session):
        self.banco = banco

    def _converter_para_entidade(
        self,
        modelo: ModeloVeiculo,
    ) -> Veiculo:
        return Veiculo(
            id=modelo.id,
            marca=modelo.marca,
            modelo=modelo.modelo,
            ano=modelo.ano,
            cor=modelo.cor,
            preco=modelo.preco,
            status=StatusVeiculo(modelo.status),
            criado_em=modelo.criado_em,
            atualizado_em=modelo.atualizado_em,
        )

    def cadastrar(self, veiculo: Veiculo) -> Veiculo:
        modelo = ModeloVeiculo(
            id=veiculo.id,
            marca=veiculo.marca,
            modelo=veiculo.modelo,
            ano=veiculo.ano,
            cor=veiculo.cor,
            preco=veiculo.preco,
            status=veiculo.status.value,
        )

        try:
            self.banco.add(modelo)
            self.banco.commit()
            self.banco.refresh(modelo)

            return self._converter_para_entidade(modelo)

        except Exception:
            self.banco.rollback()
            raise

    def consultar_por_id(self, veiculo_id: UUID) -> Veiculo | None:
        modelo = self.banco.get(ModeloVeiculo, veiculo_id)

        if modelo is None:
            return None

        return self._converter_para_entidade(modelo)

    def editar(self, veiculo: Veiculo) -> Veiculo:
        modelo = self.banco.get(ModeloVeiculo, veiculo.id)

        if modelo is None:
            raise ValueError("Veículo não encontrado.")

        modelo.marca = veiculo.marca
        modelo.modelo = veiculo.modelo
        modelo.ano = veiculo.ano
        modelo.cor = veiculo.cor
        modelo.preco = veiculo.preco
        modelo.status = veiculo.status.value

        try:
            self.banco.commit()
            self.banco.refresh(modelo)

            return self._converter_para_entidade(modelo)

        except Exception:
            self.banco.rollback()
            raise

    def listar(
        self,
        status: StatusVeiculo | None = None,
    ) -> list[Veiculo]:
        consulta = select(ModeloVeiculo)

        if status is not None:
            consulta = consulta.where(ModeloVeiculo.status == status.value)

        consulta = consulta.order_by(ModeloVeiculo.preco.asc())

        modelos = self.banco.scalars(consulta).all()

        return [self._converter_para_entidade(modelo) for modelo in modelos]
