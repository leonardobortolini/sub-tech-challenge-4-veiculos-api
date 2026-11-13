from enum import Enum


class StatusVeiculo(str, Enum):
    DISPONIVEL = "DISPONIVEL"
    RESERVADO = "RESERVADO"
    VENDIDO = "VENDIDO"