from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Categoria
from app.schemas import CategoriaCreate, CategoriaRead
from typing import List, Optional
import logging

router = APIRouter(prefix="/categorias", tags=["Categorias"])

@router.post("/", response_model=CategoriaRead)
def criar_categoria(categoria: CategoriaCreate, session: Session = Depends(get_session)):
    db_categoria = Categoria.from_orm(categoria)
    session.add(db_categoria)
    session.commit()
    session.refresh(db_categoria)
    logging.info(f"Categoria criada: {db_categoria.nome} (id={db_categoria.id})")
    return db_categoria

@router.get("/", response_model=List[CategoriaRead])
def listar_categorias(page: int = 1, limit: int = 10, session: Session = Depends(get_session)):
    skip = (page - 1) * limit
    categorias = session.exec(select(Categoria).offset(skip).limit(limit)).all()
    return categorias

@router.get("/contagem")
def contar_categorias(session: Session = Depends(get_session)):
    quantidade = session.exec(select(Categoria)).all()
    return {"quantidade": len(quantidade)}

@router.get("/filtrar", response_model=List[CategoriaRead])
def filtrar_categorias(
    nome: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    session: Session = Depends(get_session)
):
    skip = (page - 1) * limit
    query = select(Categoria)
    if nome:
        query = query.where(Categoria.nome.ilike(f"%{nome}%"))
    categorias = session.exec(query.offset(skip).limit(limit)).all()
    return categorias

@router.get("/{categoria_id}", response_model=CategoriaRead)
def buscar_categoria(categoria_id: int, session: Session = Depends(get_session)):
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return categoria

@router.put("/{categoria_id}", response_model=CategoriaRead)
def atualizar_categoria(categoria_id: int, dados: CategoriaCreate, session: Session = Depends(get_session)):
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        logging.warning(f"Update falhou: Categoria não encontrada (id={categoria_id})")
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    for key, value in dados.dict().items():
        setattr(categoria, key, value)
    session.commit()
    session.refresh(categoria)
    logging.info(f"Categoria atualizada: {categoria.nome} (id={categoria.id})")
    return categoria

@router.delete("/{categoria_id}")
def deletar_categoria(categoria_id: int, session: Session = Depends(get_session)):
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        logging.warning(f"Tentativa de deletar categoria inexistente (id={categoria_id})")
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    session.delete(categoria)
    session.commit()
    logging.info(f"Categoria deletada: {categoria.nome} (id={categoria.id})")
    return {"ok": True, "message": "Categoria deletada"}

