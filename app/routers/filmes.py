from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.database import get_session
from app.models import Filme, Categoria, FilmeCategoriaLink
from app.schemas import FilmeCreate, FilmeRead, CategoriaRead
from typing import List, Optional
import logging


router = APIRouter(prefix="/filmes", tags=["Filmes"])

@router.post("/", response_model=FilmeRead)
def criar_filme(filme: FilmeCreate, session: Session = Depends(get_session)):
    db_filme = Filme(
        titulo=filme.titulo,
        ano=filme.ano,
        duracao=filme.duracao,
        classificacao=filme.classificacao,
        sinopse=filme.sinopse,
    )
    session.add(db_filme)
    session.commit()
    session.refresh(db_filme)

    if filme.categoria_ids:
        for cat_id in filme.categoria_ids:
            link = FilmeCategoriaLink(filme_id=db_filme.id, categoria_id=cat_id)
            session.add(link)
        session.commit()
    session.refresh(db_filme)
    logging.info(f"Filme criado: {db_filme.titulo} (id={db_filme.id})")
    return db_filme

@router.get("/", response_model=List[FilmeRead])
def listar_filmes(page: int = 1, limit: int = 10, session: Session = Depends(get_session)):
    skip = (page - 1) * limit
    filmes = session.exec(select(Filme).offset(skip).limit(limit)).all()
    return filmes

@router.get("/contagem")
def contar_filmes(session: Session = Depends(get_session)):
    quantidade = session.exec(select(Filme)).all()
    return {"quantidade": len(quantidade)}


@router.get("/filtrar", response_model=List[FilmeRead])
def filtrar_filmes(
    titulo: Optional[str] = None,
    categoria_id: Optional[int] = None,
    ano_min: Optional[int] = None,
    ano_max: Optional[int] = None,
    page: int = 1,
    limit: int = 10,
    session: Session = Depends(get_session)
):
    skip = (page - 1) * limit
    query = select(Filme)

    if titulo:
        query = query.where(Filme.titulo.ilike(f"%{titulo}%"))
    if categoria_id:
        query = query.join(Filme.categorias).where(Categoria.id == categoria_id)
    if ano_min:
        query = query.where(Filme.ano >= ano_min)
    if ano_max:
        query = query.where(Filme.ano <= ano_max)

    filmes = session.exec(query.offset(skip).limit(limit)).all()
    return filmes

@router.get("/{filme_id}", response_model=FilmeRead)
def buscar_filme(filme_id: int, session: Session = Depends(get_session)):
    filme = session.get(Filme, filme_id)
    if not filme:
        raise HTTPException(status_code=404, detail="Filme não encontrado")
    return filme

@router.put("/{filme_id}", response_model=FilmeRead)
def atualizar_filme(filme_id: int, dados: FilmeCreate, session: Session = Depends(get_session)):
    filme = session.get(Filme, filme_id)
    if not filme:
        logging.warning(f"Update falhou: Filme não encontrado (id={filme_id})")
        raise HTTPException(status_code=404, detail="Filme não encontrado")
    for key, value in dados.dict(exclude={"categoria_ids"}).items():
        setattr(filme, key, value)
    session.commit()
    if dados.categoria_ids is not None:
        session.exec(
            select(FilmeCategoriaLink).where(FilmeCategoriaLink.filme_id == filme_id)
        ).delete()
        for cat_id in dados.categoria_ids:
            link = FilmeCategoriaLink(filme_id=filme_id, categoria_id=cat_id)
            session.add(link)
        session.commit()
    session.refresh(filme)
    logging.info(f"Filme atualizado: {filme.titulo} (id={filme.id})")
    return filme

@router.delete("/{filme_id}")
def deletar_filme(filme_id: int, session: Session = Depends(get_session)):
    filme = session.get(Filme, filme_id)
    if not filme:
        logging.warning(f"Tentativa de deletar filme inexistente (id={filme_id})")
        raise HTTPException(status_code=404, detail="Filme não encontrado")
    session.delete(filme)
    session.commit()
    logging.info(f"Filme deletado: {filme.titulo} (id={filme.id})")
    return {"ok": True, "message": "Filme deletado"}



