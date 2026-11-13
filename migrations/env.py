
from logging.config import fileConfig

from alembic import context

from app.infrastructure.config import configuracoes
from app.infrastructure.database import Base, engine
from app.infrastructure.modelos import ModeloVeiculo  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata utilizada pelo Alembic para identificar alterações nos modelos.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Executa migrations sem estabelecer uma conexão com o banco."""

    context.configure(
        url=configuracoes.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa migrations utilizando a conexão com o banco."""

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
