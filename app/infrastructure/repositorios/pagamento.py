
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entidades.pagamento import Pagamento
from app.domain.enums.status_pagamento import StatusPagamento
from app.domain.repositorios.pagamento import RepositorioPagamento
from app.infrastructure.modelos.pagamento import ModeloPagamento


class RepositorioPagamentoSQLAlchemy(RepositorioPagamento):

    def __init__(self, banco: Session):
        self.banco = banco

    @staticmethod
    def _para_entidade(modelo: ModeloPagamento) -> Pagamento:
        return Pagamento(
            id=modelo.id,
            veiculo_id=modelo.veiculo_id,
            cpf=modelo.cpf,
            valor=modelo.valor,
            status=StatusPagamento(modelo.status),
            criado_em=modelo.criado_em,
            atualizado_em=modelo.atualizado_em,
        )

    def cadastrar(self, pagamento: Pagamento) -> Pagamento:
        modelo = ModeloPagamento(
            id=pagamento.id,
            veiculo_id=pagamento.veiculo_id,
            cpf=pagamento.cpf,
            valor=pagamento.valor,
            status=pagamento.status.value,
        )

        try:
            self.banco.add(modelo)
            self.banco.commit()
            self.banco.refresh(modelo)
            return self._para_entidade(modelo)
        except Exception:
            self.banco.rollback()
            raise

    def editar(self, pagamento: Pagamento) -> Pagamento:
        modelo = self.banco.get(ModeloPagamento, pagamento.id)

        if modelo is None:
            raise ValueError("Pagamento não encontrado.")

        modelo.status = pagamento.status.value

        try:
            self.banco.commit()
            self.banco.refresh(modelo)
            return self._para_entidade(modelo)
        except Exception:
            self.banco.rollback()
            raise

    def consultar_por_id(
        self,
        pagamento_id: UUID,
    ) -> Pagamento | None:
        modelo = self.banco.get(ModeloPagamento, pagamento_id)

        if modelo is None:
            return None

        return self._para_entidade(modelo)

    def consultar_por_veiculo(
        self,
        veiculo_id: UUID,
    ) -> list[Pagamento]:
        consulta = (
            select(ModeloPagamento)
            .where(ModeloPagamento.veiculo_id == veiculo_id)
            .order_by(ModeloPagamento.criado_em.desc())
        )

        modelos = self.banco.scalars(consulta).all()

        return [
            self._para_entidade(modelo)
            for modelo in modelos
        ]

    def consultar_pendente_por_veiculo(
        self,
        veiculo_id: UUID,
    ) -> Pagamento | None:
        consulta = select(ModeloPagamento).where(
            ModeloPagamento.veiculo_id == veiculo_id,
            ModeloPagamento.status == StatusPagamento.PENDENTE.value,
        )

        modelo = self.banco.scalar(consulta)

        if modelo is None:
            return None

        return self._para_entidade(modelo)
