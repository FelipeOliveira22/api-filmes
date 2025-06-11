from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Locacao, Filme, Cliente
from app.schemas import LocacaoCreate, LocacaoRead, FilmeRead
from typing import List, Optional
import logging
from app.models import LocacaoFilmeLink

router = APIRouter(prefix="/locacoes", tags=["Locações"])

@router.post("/", response_model=LocacaoRead)
def criar_locacao(locacao: LocacaoCreate, session: Session = Depends(get_session)):
    db_locacao = Locacao(
        cliente_id=locacao.cliente_id,
        data_retirada=locacao.data_retirada,
        data_devolucao=locacao.data_devolucao,
        valor=locacao.valor,
        status=locacao.status,
    )
    session.add(db_locacao)
    session.commit()
    session.refresh(db_locacao)

    if locacao.filme_ids:
        for filme_id in locacao.filme_ids:
            link = LocacaoFilmeLink(locacao_id=db_locacao.id, filme_id=filme_id)
            session.add(link)
        session.commit()
    session.refresh(db_locacao)
    logging.info(f"Locação criada: id={db_locacao.id}, cliente_id={db_locacao.cliente_id}")
    return db_locacao


@router.get("/", response_model=List[LocacaoRead])
def listar_locacoes(page: int = 1, limit: int = 10, session: Session = Depends(get_session)):
    skip = (page - 1) * limit
    locacoes = session.exec(select(Locacao).offset(skip).limit(limit)).all()
    return locacoes

@router.get("/contagem")
def contar_locacoes(session: Session = Depends(get_session)):
    quantidade = session.exec(select(Locacao)).all()
    return {"quantidade": len(quantidade)}

@router.get("/filtrar", response_model=List[LocacaoRead])
def filtrar_locacoes(
    status: Optional[str] = None,
    cliente_id: Optional[int] = None,
    page: int = 1,
    limit: int = 10,
    session: Session = Depends(get_session)
):
    skip = (page - 1) * limit
    query = select(Locacao)
    if status:
        query = query.where(Locacao.status == status)
    if cliente_id:
        query = query.where(Locacao.cliente_id == cliente_id)
    locacoes = session.exec(query.offset(skip).limit(limit)).all()
    return locacoes

@router.get("/filtrar-avancado", response_model=List[LocacaoRead])
def filtrar_locacoes_avancado(
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    session: Session = Depends(get_session)
):
    query = select(Locacao)


    if data_inicio:
        query = query.where(Locacao.data_retirada >= data_inicio)
    if data_fim:
        query = query.where(Locacao.data_retirada <= data_fim)

    locacoes = session.exec(query).all()
    return locacoes

@router.get("/{locacao_id}", response_model=LocacaoRead)
def buscar_locacao(locacao_id: int, session: Session = Depends(get_session)):
    locacao = session.get(Locacao, locacao_id)
    if not locacao:
        raise HTTPException(status_code=404, detail="Locação não encontrada")
    filme_ids = [link.filme_id for link in locacao.filmes]
    return LocacaoRead(
        id=locacao.id,
        cliente_id=locacao.cliente_id,
        data_retirada=locacao.data_retirada,
        data_devolucao=locacao.data_devolucao,
        valor=locacao.valor,
        status=locacao.status,
        filme_ids=filme_ids
    )


@router.put("/{locacao_id}", response_model=LocacaoRead)
def atualizar_locacao(locacao_id: int, dados: LocacaoCreate, session: Session = Depends(get_session)):
    locacao = session.get(Locacao, locacao_id)
    if not locacao:
        logging.warning(f"Update falhou: Locação não encontrada (id={locacao_id})")
        raise HTTPException(status_code=404, detail="Locação não encontrada")
    for key, value in dados.dict(exclude={"filme_ids"}).items():
        setattr(locacao, key, value)
    if dados.filme_ids is not None:
        session.exec(
        select(LocacaoFilmeLink).where(LocacaoFilmeLink.locacao_id == locacao.id)
    ).delete()
    for filme_id in dados.filme_ids:
        link = LocacaoFilmeLink(locacao_id=locacao.id, filme_id=filme_id)
        session.add(link)
    session.commit()

    session.refresh(locacao)
    logging.info(f"Locação atualizada: id={locacao.id}, cliente_id={locacao.cliente_id}")
    return locacao

@router.delete("/{locacao_id}")
def deletar_locacao(locacao_id: int, session: Session = Depends(get_session)):
    locacao = session.get(Locacao, locacao_id)
    if not locacao:
        logging.warning(f"Tentativa de deletar locação inexistente (id={locacao_id})")
        raise HTTPException(status_code=404, detail="Locação não encontrada")
    session.delete(locacao)
    session.commit()
    logging.info(f"Locação deletada: id={locacao.id}")
    return {"ok": True, "message": "Locação deletada"}

