import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.database import Base, get_db
from app.infrastructure.modelos import (
    ModeloPagamento,  # noqa: F401
    ModeloVeiculo,  # noqa: F401
)
from app.main import app


@pytest.fixture
def banco_teste():

    engine_teste = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SessaoTeste = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine_teste,
    )

    Base.metadata.create_all(bind=engine_teste)

    banco = SessaoTeste()

    yield banco

    banco.close()

    Base.metadata.drop_all(bind=engine_teste)
    engine_teste.dispose()


@pytest.fixture
def cliente(banco_teste):

    def substituir_banco():
        yield banco_teste

    app.dependency_overrides[get_db] = substituir_banco

    with TestClient(app) as cliente_teste:
        yield cliente_teste

    app.dependency_overrides.clear()