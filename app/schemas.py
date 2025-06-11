from pydantic import BaseModel
from typing import Optional, List

class ClienteBase(BaseModel):
    nome: str
    cpf: str
    email: str
    telefone: str
    endereco: str

class ClienteCreate(ClienteBase):
    pass

class ClienteRead(ClienteBase):
    id: int

class CategoriaBase(BaseModel):
    nome: str
    descricao: str

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaRead(CategoriaBase):
    id: int

class FilmeBase(BaseModel):
    titulo: str
    ano: int
    duracao: int
    classificacao: str
    sinopse: str

class FilmeCreate(FilmeBase):
    categoria_ids: Optional[List[int]] = []

class FilmeRead(FilmeBase):
    id: int
    categorias: Optional[List[CategoriaRead]] = []

class LocacaoBase(BaseModel):
    cliente_id: int
    data_retirada: str
    data_devolucao: Optional[str]
    valor: float
    status: str

class LocacaoCreate(LocacaoBase):
    filme_ids: Optional[List[int]] = []

class LocacaoRead(BaseModel):
    id: int
    cliente_id: int
    data_retirada: str
    data_devolucao: Optional[str]
    valor: float
    status: str
    filme_ids: List[int] = []


class PagamentoBase(BaseModel):
    locacao_id: int
    data_pagamento: str
    valor_pago: float
    forma_pagamento: str
    status: str

class PagamentoCreate(PagamentoBase):
    pass

class PagamentoRead(PagamentoBase):
    id: int
