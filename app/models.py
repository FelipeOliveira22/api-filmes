from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class FilmeCategoriaLink(SQLModel, table=True):
    filme_id: Optional[int] = Field(default=None, foreign_key="filme.id", primary_key=True)
    categoria_id: Optional[int] = Field(default=None, foreign_key="categoria.id", primary_key=True)

class Categoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    descricao: str

    filmes: List["Filme"] = Relationship(
        back_populates="categorias",
        link_model=FilmeCategoriaLink
    )

class Filme(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    ano: int
    duracao: int
    classificacao: str
    sinopse: str

    categorias: List[Categoria] = Relationship(
        back_populates="filmes",
        link_model=FilmeCategoriaLink
    )

    locacoes: List["LocacaoFilmeLink"] = Relationship(
        back_populates="filme"
    )

class Cliente(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    cpf: str
    email: str
    telefone: str
    endereco: str

    locacoes: List["Locacao"] = Relationship(
        back_populates="cliente"
    )
class LocacaoFilmeLink(SQLModel, table=True):
    locacao_id: Optional[int] = Field(default=None, foreign_key="locacao.id", primary_key=True)
    filme_id: Optional[int] = Field(default=None, foreign_key="filme.id", primary_key=True)
    filme: Optional["Filme"] = Relationship(back_populates="locacoes")
    locacao: Optional["Locacao"] = Relationship(back_populates="filmes")

class Locacao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cliente_id: int = Field(foreign_key="cliente.id")
    data_retirada: str
    data_devolucao: Optional[str]
    valor: float
    status: str

    cliente: Optional["Cliente"] = Relationship(back_populates="locacoes")
    filmes: List[LocacaoFilmeLink] = Relationship(back_populates="locacao")
    pagamento: Optional["Pagamento"] = Relationship(back_populates="locacao")

class Pagamento(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    locacao_id: int = Field(foreign_key="locacao.id", unique=True)
    data_pagamento: str
    valor_pago: float
    forma_pagamento: str
    status: str

    locacao: Optional[Locacao] = Relationship(back_populates="pagamento")
