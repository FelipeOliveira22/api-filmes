from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Pagamento
from app.schemas import PagamentoCreate, PagamentoRead
from typing import List, Optional
import logging


router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])

@router.post("/", response_model=PagamentoRead)
def criar_pagamento(pagamento: PagamentoCreate, session: Session = Depends(get_session)):
    db_pagamento = Pagamento.from_orm(pagamento)
    session.add(db_pagamento)
    session.commit()
    session.refresh(db_pagamento)
    logging.info(f"Pagamento criado: id={db_pagamento.id}, locacao_id={db_pagamento.locacao_id}")
    return db_pagamento

@router.get("/", response_model=List[PagamentoRead])
def listar_pagamentos(page: int = 1, limit: int = 10, session: Session = Depends(get_session)):
    skip = (page - 1) * limit
    pagamentos = session.exec(select(Pagamento).offset(skip).limit(limit)).all()
    return pagamentos

@router.get("/contagem")
def contar_pagamentos(session: Session = Depends(get_session)):
    quantidade = session.exec(select(Pagamento)).all()
    return {"quantidade": len(quantidade)}

@router.get("/filtrar", response_model=List[PagamentoRead])
def filtrar_pagamentos(
    status: Optional[str] = None,
    forma_pagamento: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    session: Session = Depends(get_session)
):
    skip = (page - 1) * limit
    query = select(Pagamento)
    if status:
        query = query.where(Pagamento.status == status)
    if forma_pagamento:
        query = query.where(Pagamento.forma_pagamento == forma_pagamento)
    pagamentos = session.exec(query.offset(skip).limit(limit)).all()
    return pagamentos

@router.get("/filtrar-avancado", response_model=List[PagamentoRead])
def filtrar_pagamentos_avancado(
    status: Optional[str] = None,
    forma_pagamento: Optional[str] = None,
    valor_min: Optional[float] = None,
    valor_max: Optional[float] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    session: Session = Depends(get_session)
):
    query = select(Pagamento)
    if status:
        query = query.where(Pagamento.status == status)
    if forma_pagamento:
        query = query.where(Pagamento.forma_pagamento == forma_pagamento)
    if valor_min is not None:
        query = query.where(Pagamento.valor_pago >= valor_min)
    if valor_max is not None:
        query = query.where(Pagamento.valor_pago <= valor_max)
    if data_inicio:
        query = query.where(Pagamento.data_pagamento >= data_inicio)
    if data_fim:
        query = query.where(Pagamento.data_pagamento <= data_fim)
    pagamentos = session.exec(query).all()
    return pagamentos

@router.get("/total-pago")
def total_pago(
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    session: Session = Depends(get_session)
):
    query = select(Pagamento)
    if data_inicio:
        query = query.where(Pagamento.data_pagamento >= data_inicio)
    if data_fim:
        query = query.where(Pagamento.data_pagamento <= data_fim)
    pagamentos = session.exec(query).all()
    total = sum(p.valor_pago for p in pagamentos)
    return {"total_pago": total}


@router.get("/{pagamento_id}", response_model=PagamentoRead)
def buscar_pagamento(pagamento_id: int, session: Session = Depends(get_session)):
    pagamento = session.get(Pagamento, pagamento_id)
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    return pagamento

@router.put("/{pagamento_id}", response_model=PagamentoRead)
def atualizar_pagamento(pagamento_id: int, dados: PagamentoCreate, session: Session = Depends(get_session)):
    pagamento = session.get(Pagamento, pagamento_id)
    if not pagamento:
        logging.warning(f"Update falhou: Pagamento não encontrado (id={pagamento_id})")
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    for key, value in dados.dict().items():
        setattr(pagamento, key, value)
    session.commit()
    session.refresh(pagamento)
    logging.info(f"Pagamento atualizado: id={pagamento.id}")
    return pagamento

@router.delete("/{pagamento_id}")
def deletar_pagamento(pagamento_id: int, session: Session = Depends(get_session)):
    pagamento = session.get(Pagamento, pagamento_id)
    if not pagamento:
        logging.warning(f"Tentativa de deletar pagamento inexistente (id={pagamento_id})")
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    session.delete(pagamento)
    session.commit()
    logging.info(f"Pagamento deletado: id={pagamento.id}")
    return {"ok": True, "message": "Pagamento deletado"}

