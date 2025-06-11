from fastapi import FastAPI
from app.routers import filmes, clientes, locacoes, pagamentos, categorias
from app.database import create_db_and_tables
from app import logging_config  


app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(filmes.router)
app.include_router(clientes.router)
app.include_router(locacoes.router)
app.include_router(pagamentos.router)
app.include_router(categorias.router)
