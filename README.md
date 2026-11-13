# Veículos API

API responsável pelo gerenciamento de veículos.

## Tecnologias

- Python 3.12
- FastAPI
- SQLAlchemy
- PostgreSQL 16
- Alembic
- Docker e Docker Compose
- Pytest
- Ruff

## Funcionalidades

- Cadastro, consulta e edição de veículos.
- Listagem de veículos por status.
- Ordenação dos veículos por preço crescente.
- Solicitação e consulta de pagamentos.
- Recebimento de notificações de pagamento via webhook.
- Integração HTTP com o microsserviço de vendas.

## Estrutura do projeto

O serviço utiliza uma arquitetura baseada em Domain-Driven Design (DDD), organizada em:

- `domain`: entidades e regras de negócio.
- `application`: casos de uso e interfaces.
- `infrastructure`: banco de dados, repositórios e integrações.
- `interfaces`: rotas e schemas da API.
- `migrations`: versionamento do banco de dados com Alembic.
- `tests`: testes automatizados.

## Como executar

### Pré-requisitos

- Docker
- Docker Compose

### Inicialização

Inicie a aplicação:

```bash
docker compose up -d --build
```

O Docker Compose inicia a API e o PostgreSQL. As migrations do Alembic são executadas automaticamente antes da inicialização da aplicação.

A API estará disponível em:

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health check: http://localhost:8000/health

Para visualizar os logs:

```bash
docker compose logs -f api
```

Para interromper os serviços:

```bash
docker compose down
```

## Endpoints

### Veículos

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/veiculos` | Lista os veículos cadastrados |
| POST | `/veiculos` | Cadastra um veículo |
| GET | `/veiculos/{veiculo_id}` | Consulta um veículo pelo ID |
| PUT | `/veiculos/{veiculo_id}` | Edita os dados de um veículo |

A listagem aceita o parâmetro opcional `status`, com os valores:

- `DISPONIVEL`
- `RESERVADO`
- `VENDIDO`

Os resultados são ordenados por preço crescente.

Exemplo:

```http
GET /veiculos?status=DISPONIVEL
```

### Pagamentos

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/pagamentos` | Solicita um pagamento |
| GET | `/pagamentos/{pagamento_id}` | Consulta um pagamento pelo ID |
| POST | `/pagamentos/webhook` | Recebe notificações de pagamento |

O webhook permite receber atualizações sobre o processamento do pagamento, como aprovação ou cancelamento.

Para consultar os parâmetros, schemas e respostas de cada endpoint, acesse o Swagger.

## Testes e qualidade

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute os testes:

```bash
pytest
```

Execute a análise de cobertura:

```bash
pytest --cov=app --cov-branch --cov-report=term-missing
```

Execute o Ruff:

```bash
ruff check app tests
```

## CI/CD

O projeto utiliza GitHub Actions para automação de integração e entrega contínua.

- **CI:** executa análise estática com Ruff e testes automatizados em Pull Requests e atualizações da branch `main`.
- **CD:** após a conclusão bem-sucedida do CI na `main`, constrói a imagem Docker, inicia os containers, verifica o endpoint `/health` e realiza a limpeza do ambiente de execução.

## Integração com outros serviços

Este microsserviço integra-se ao `vendas-api` por meio de comunicação HTTP.

A rede Docker compartilhada `microsservicos` permite a comunicação entre os containers.

O serviço de veículos deve ser iniciado primeiro, pois é responsável pela criação dessa rede compartilhada.