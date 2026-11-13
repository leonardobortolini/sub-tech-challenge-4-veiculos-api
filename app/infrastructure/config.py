from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracoes(BaseSettings):
    database_url: str = "postgresql+psycopg://veiculos:veiculos@localhost:5432/veiculos"

    vendas_api_url: str = "http://localhost:8001"

    model_config = SettingsConfigDict(
        case_sensitive=False,
    )


configuracoes = Configuracoes()
