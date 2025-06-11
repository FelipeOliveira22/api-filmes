# Felipe Oliveira Nogueira (535783)
# Caio Rian Reinaldo de Sousa (539098)
---
# API de Locadora de Filmes

## Funcionalidades

- CRUD completo para Clientes, Filmes, Categorias, Locações e Pagamentos
- Relacionamentos 1:1, 1:N e N:N (usando tabelas de associação)
- Paginação e filtragem em todos os endpoints de listagem
- Contagem de registros por entidade
- Migrações de banco com Alembic
- Sistema de logs para monitoramento das operações

---

## Pré-requisitos

- Python 3.10 ou superior
- Git

---

## Rodar Ambiente

- pip install -r requirements.txt
- uv venv
- uv sync
- uvicorn app.main:app --reload

## Alambic

- alembic revision --autogenerate -m "Passar o Comando aqui de acordo com qual migration você (usuário) quer realizar, aqui no nosso projeto foi passado algo, como: "Criação campo xyz"
- alembic upgrade head

---
