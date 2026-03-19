from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import models, schemas
from app.auth import get_current_user

router = APIRouter(prefix="/servicos", tags=["Servicos"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔐 CREATE SERVIÇO
@router.post("/", response_model=schemas.ServicoResponse)
def create_servico(
    servico: schemas.ServicoCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):

    db_servico = models.Servico(
        salon_id=current_user.salon_id,
        nome=servico.nome,
        preco=servico.preco,
        duracao=servico.duracao,
    )

    db.add(db_servico)
    db.commit()
    db.refresh(db_servico)

    return db_servico


# 🔐 LISTAR SERVIÇOS
@router.get("/", response_model=list[schemas.ServicoResponse])
def list_servicos(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):

    return db.query(models.Servico).filter(
        models.Servico.salon_id == current_user.salon_id
    ).all()


# 🔐 UPDATE SERVIÇO
@router.put("/{servico_id}", response_model=schemas.ServicoResponse)
def update_servico(
    servico_id: int,
    servico: schemas.ServicoCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):

    db_servico = db.query(models.Servico).filter(
        models.Servico.id == servico_id,
        models.Servico.salon_id == current_user.salon_id
    ).first()

    if not db_servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    db_servico.nome = servico.nome
    db_servico.preco = servico.preco
    db_servico.duracao = servico.duracao

    db.commit()
    db.refresh(db_servico)

    return db_servico


# 🔐 DELETE SERVIÇO
@router.delete("/{servico_id}")
def deletar_servico(
    servico_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):

    servico = db.query(models.Servico).filter(
        models.Servico.id == servico_id,
        models.Servico.salon_id == current_user.salon_id
    ).first()

    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    db.delete(servico)
    db.commit()

    return {"mensagem": "Serviço deletado com sucesso"}

@router.get("/salon/{salon_id}")
def get_servicos_por_salao(salon_id: int, db: Session = Depends(get_db)):
    return db.query(models.Servico)\
        .filter(models.Servico.salon_id == salon_id)\
        .all()
