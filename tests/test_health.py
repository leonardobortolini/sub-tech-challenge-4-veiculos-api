from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.main import app
from app.infrastructure.database import get_db


cliente = TestClient(app)


def test_verificar_saude_com_sucesso(monkeypatch):

    conexao = MagicMock()
    conexao_contexto = MagicMock()
    conexao_contexto.__enter__.return_value = conexao

    monkeypatch.setattr(
        "app.main.engine.connect",
        lambda: conexao_contexto,
    )

    resposta = cliente.get("/health")

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "saudavel"


def test_verificar_saude_com_falha_no_banco(monkeypatch):

    def simular_falha():
        raise SQLAlchemyError("Banco indisponível")

    monkeypatch.setattr(
        "app.main.engine.connect",
        simular_falha,
    )

    resposta = cliente.get("/health")

    assert resposta.status_code == 503
    assert resposta.json()["detail"]["status"] == "indisponivel"


def test_sessao_do_banco_e_fechada(monkeypatch):

    sessao = MagicMock()

    monkeypatch.setattr(
        "app.infrastructure.database.SessaoLocal",
        lambda: sessao,
    )

    gerador = get_db()

    assert next(gerador) is sessao

    try:
        next(gerador)
    except StopIteration:
        pass

    sessao.close.assert_called_once()