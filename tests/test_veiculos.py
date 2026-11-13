from uuid import UUID

from app.infrastructure.modelos import ModeloVeiculo


def test_cadastrar_veiculo(cliente):
    resposta = cliente.post(
        "/veiculos",
        json={
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2024,
            "cor": "Preto",
            "preco": "145000.00",
        },
    )

    assert resposta.status_code == 201

    dados = resposta.json()

    assert dados["marca"] == "Toyota"
    assert dados["modelo"] == "Corolla"
    assert dados["ano"] == 2024
    assert dados["cor"] == "Preto"
    assert dados["status"] == "DISPONIVEL"
    assert dados["id"] is not None


def test_consultar_veiculo(cliente):
    cadastro = cliente.post(
        "/veiculos",
        json={
            "marca": "Honda",
            "modelo": "Civic",
            "ano": 2023,
            "cor": "Branco",
            "preco": "130000.00",
        },
    )

    veiculo_id = cadastro.json()["id"]

    resposta = cliente.get(f"/veiculos/{veiculo_id}")

    assert resposta.status_code == 200
    assert resposta.json()["modelo"] == "Civic"


def test_editar_veiculo(cliente):
    cadastro = cliente.post(
        "/veiculos",
        json={
            "marca": "Volkswagen",
            "modelo": "Golf",
            "ano": 2022,
            "cor": "Azul",
            "preco": "110000.00",
        },
    )

    veiculo_id = cadastro.json()["id"]

    resposta = cliente.put(
        f"/veiculos/{veiculo_id}",
        json={
            "marca": "Volkswagen",
            "modelo": "Golf GTI",
            "ano": 2023,
            "cor": "Vermelho",
            "preco": "150000.00",
        },
    )

    assert resposta.status_code == 200
    assert resposta.json()["modelo"] == "Golf GTI"
    assert resposta.json()["preco"] == "150000.00"


def test_consultar_veiculo_inexistente(cliente):
    veiculo_id = "00000000-0000-0000-0000-000000000001"

    resposta = cliente.get(f"/veiculos/{veiculo_id}")

    assert resposta.status_code == 404


def test_editar_veiculo_inexistente(cliente):
    veiculo_id = "00000000-0000-0000-0000-000000000001"

    resposta = cliente.put(
        f"/veiculos/{veiculo_id}",
        json={
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2024,
            "cor": "Preto",
            "preco": "145000.00",
        },
    )

    assert resposta.status_code == 404


def test_nao_editar_veiculo_reservado(cliente, banco_teste):
    cadastro = cliente.post(
        "/veiculos",
        json={
            "marca": "Ford",
            "modelo": "Mustang",
            "ano": 2024,
            "cor": "Preto",
            "preco": "350000.00",
        },
    )

    veiculo_id = UUID(cadastro.json()["id"])

    veiculo = banco_teste.get(ModeloVeiculo, veiculo_id)
    veiculo.status = "RESERVADO"
    banco_teste.commit()

    resposta = cliente.put(
        f"/veiculos/{veiculo_id}",
        json={
            "marca": "Ford",
            "modelo": "Mustang",
            "ano": 2024,
            "cor": "Branco",
            "preco": "360000.00",
        },
    )

    assert resposta.status_code == 409


def test_nao_cadastrar_veiculo_com_preco_negativo(cliente):
    resposta = cliente.post(
        "/veiculos",
        json={
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2024,
            "cor": "Preto",
            "preco": "-100.00",
        },
    )

    assert resposta.status_code == 422


def test_nao_cadastrar_veiculo_com_marca_vazia(cliente):
    resposta = cliente.post(
        "/veiculos",
        json={
            "marca": "   ",
            "modelo": "Corolla",
            "ano": 2024,
            "cor": "Preto",
            "preco": "145000.00",
        },
    )

    assert resposta.status_code == 422


def test_nao_cadastrar_veiculo_com_ano_invalido(cliente):
    resposta = cliente.post(
        "/veiculos",
        json={
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 1800,
            "cor": "Preto",
            "preco": "145000.00",
        },
    )

    assert resposta.status_code == 422


def test_listar_veiculos_ordenados_por_preco(cliente):
    veiculos = [
        ("Toyota", "Corolla", "145000.00"),
        ("Honda", "Civic", "130000.00"),
        ("Volkswagen", "Golf", "110000.00"),
    ]

    for marca, modelo, preco in veiculos:
        resposta = cliente.post(
            "/veiculos",
            json={
                "marca": marca,
                "modelo": modelo,
                "ano": 2024,
                "cor": "Preto",
                "preco": preco,
            },
        )
        assert resposta.status_code == 201

    resposta = cliente.get("/veiculos")

    assert resposta.status_code == 200

    dados = resposta.json()

    assert [veiculo["modelo"] for veiculo in dados] == [
        "Golf",
        "Civic",
        "Corolla",
    ]


def test_listar_veiculos_por_status_disponivel(cliente):
    cliente.post(
        "/veiculos",
        json={
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano": 2024,
            "cor": "Preto",
            "preco": "145000.00",
        },
    )

    resposta = cliente.get("/veiculos?status=DISPONIVEL")

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["status"] == "DISPONIVEL"


def test_listar_veiculos_por_status_vendido(cliente, banco_teste):
    cadastro = cliente.post(
        "/veiculos",
        json={
            "marca": "Honda",
            "modelo": "Civic",
            "ano": 2024,
            "cor": "Preto",
            "preco": "130000.00",
        },
    )

    veiculo = banco_teste.get(
        ModeloVeiculo,
        UUID(cadastro.json()["id"]),
    )
    veiculo.status = "VENDIDO"
    banco_teste.commit()

    resposta = cliente.get("/veiculos?status=VENDIDO")

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["status"] == "VENDIDO"


def test_listar_veiculos_com_status_invalido(cliente):
    resposta = cliente.get("/veiculos?status=INVALIDO")

    assert resposta.status_code == 422
