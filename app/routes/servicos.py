from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas
from app.auth import get_current_user  # IMPORTANTE

router = APIRouter(prefix="/servicos", tags=["Servicos"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔐 CREATE SERVIÇO (PROTEGIDO E SEGURO)
@router.post("/", response_model=schemas.ServicoResponse)
def create_servico(
    servico: schemas.ServicoCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_servico = models.Servico(
        salon_id=current_user.salon_id,  # vem do token
        nome=servico.nome,
        preco=servico.preco,
        duracao=servico.duracao,
    )

    db.add(db_servico)
    db.commit()
    db.refresh(db_servico)

    return db_servico


# 🔐 LISTAR SERVIÇOS DO SALÃO LOGADO
@router.get("/", response_model=list[schemas.ServicoResponse])
def list_servicos(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Servico).filter(
        models.Servico.salon_id == current_user.salon_id
    ).all()


# 🔐 UPDATE SERVIÇO (SÓ DO PRÓPRIO SALÃO)
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
