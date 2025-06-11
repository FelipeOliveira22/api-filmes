from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.database import get_session
from app.models import Cliente
from app.schemas import ClienteCreate, ClienteRead
from typing import List, Optional
import logging

router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.post("/", response_model=ClienteRead)
def criar_cliente(cliente: ClienteCreate, session: Session = Depends(get_session)):
    db_cliente = Cliente.from_orm(cliente)
    session.add(db_cliente)
    session.commit()
    session.refresh(db_cliente)
    logging.info(f"Cliente criado: {db_cliente.nome} (id={db_cliente.id})")
    return db_cliente

@router.get("/", response_model=List[ClienteRead])
def listar_clientes(page: int = 1, limit: int = 10, session: Session = Depends(get_session)):
    skip = (page - 1) * limit
    clientes = session.exec(select(Cliente).offset(skip).limit(limit)).all()
    return clientes

@router.get("/contagem")
def contar_clientes(session: Session = Depends(get_session)):
    quantidade = session.exec(select(Cliente)).all()
    return {"quantidade": len(quantidade)}

@router.get("/filtrar", response_model=List[ClienteRead])
def filtrar_clientes(
    nome: Optional[str] = None,
    email: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    session: Session = Depends(get_session)
):
    skip = (page - 1) * limit
    query = select(Cliente)
    if nome:
        query = query.where(Cliente.nome.ilike(f"%{nome}%"))
    if email:
        query = query.where(Cliente.email.ilike(f"%{email}%"))
    clientes = session.exec(query.offset(skip).limit(limit)).all()
    return clientes

@router.get("/{cliente_id}", response_model=ClienteRead)
def buscar_cliente(cliente_id: int, session: Session = Depends(get_session)):
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

@router.put("/{cliente_id}", response_model=ClienteRead)
def atualizar_cliente(cliente_id: int, dados: ClienteCreate, session: Session = Depends(get_session)):
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        logging.warning(f"Update falhou: Cliente não encontrado (id={cliente_id})")
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    for key, value in dados.dict().items():
        setattr(cliente, key, value)
    session.commit()
    session.refresh(cliente)
    logging.info(f"Cliente atualizado: {cliente.nome} (id={cliente.id})")
    return cliente

@router.delete("/{cliente_id}")
def deletar_cliente(cliente_id: int, session: Session = Depends(get_session)):
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        logging.warning(f"Tentativa de deletar cliente inexistente (id={cliente_id})")
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    session.delete(cliente)
    session.commit()
    logging.info(f"Cliente deletado: {cliente.nome} (id={cliente.id})")
    return {"ok": True, "message": "Cliente deletado"}


