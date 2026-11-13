from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.casos_de_uso.veiculo import (
    CadastrarVeiculo,
    ConsultarVeiculo,
    EditarVeiculo,
    VeiculoNaoEncontrado,
    VeiculoNaoPodeSerEditado,
)
from app.infrastructure.database import get_db
from app.infrastructure.repositorios.veiculo import (
    RepositorioVeiculoSQLAlchemy,
)
from app.interfaces.schemas.veiculo import (
    AtualizacaoVeiculo,
    CadastroVeiculo,
    RespostaVeiculo,
)


veiculos_router = APIRouter(
    prefix="/veiculos",
    tags=["Veículos"],
)


@veiculos_router.post(
    "",
    response_model=RespostaVeiculo,
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_veiculo(
    dados: CadastroVeiculo,
    banco: Session = Depends(get_db),
):
    repositorio = RepositorioVeiculoSQLAlchemy(banco)
    caso_de_uso = CadastrarVeiculo(repositorio)

    return caso_de_uso.executar(**dados.model_dump())


@veiculos_router.get(
    "/{veiculo_id}",
    response_model=RespostaVeiculo,
)
def consultar_veiculo(
    veiculo_id: UUID,
    banco: Session = Depends(get_db),
):
    repositorio = RepositorioVeiculoSQLAlchemy(banco)
    caso_de_uso = ConsultarVeiculo(repositorio)

    try:
        return caso_de_uso.executar(veiculo_id)

    except VeiculoNaoEncontrado as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        ) from erro


@veiculos_router.put(
    "/{veiculo_id}",
    response_model=RespostaVeiculo,
)
def editar_veiculo(
    veiculo_id: UUID,
    dados: AtualizacaoVeiculo,
    banco: Session = Depends(get_db),
):
    repositorio = RepositorioVeiculoSQLAlchemy(banco)
    caso_de_uso = EditarVeiculo(repositorio)

    try:
        return caso_de_uso.executar(
            veiculo_id=veiculo_id,
            **dados.model_dump(),
        )

    except VeiculoNaoEncontrado as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        ) from erro

    except VeiculoNaoPodeSerEditado as erro:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(erro),
        ) from erro