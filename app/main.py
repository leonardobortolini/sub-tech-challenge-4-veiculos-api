from fastapi import FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.infrastructure.database import engine
from app.interfaces.rotas import veiculos_router


app = FastAPI(
    title="Veículos API"
)

app.include_router(veiculos_router)


@app.get("/health", tags=["Saúde"])
def verificar_saude():

    try:
        with engine.connect() as conexao:
            conexao.execute(text("SELECT 1"))

        return {
            "status": "saudavel",
            "servico": "veiculos-api",
            "banco_de_dados": "conectado",
        }

    except SQLAlchemyError as erro:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "indisponivel",
                "servico": "veiculos-api",
                "banco_de_dados": "desconectado",
            },
        ) from erro