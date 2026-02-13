from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas

router = APIRouter(prefix="/servicos", tags=["Servicos"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.ServicoResponse)
def create_servico(servico: schemas.ServicoCreate, db: Session = Depends(get_db)):
    db_servico = models.Servico(
        salon_id=servico.salon_id,
        nome=servico.nome,
        preco=servico.preco,
        duracao=servico.duracao,
    )
    db.add(db_servico)
    db.commit()
    db.refresh(db_servico)
    return db_servico
@router.get("/salon/{salon_id}", response_model=list[schemas.ServicoResponse])
def list_servicos(salon_id: int, db: Session = Depends(get_db)):
    servicos = db.query(models.Servico).filter(
        models.Servico.salon_id == salon_id
    ).all()
    return servicos
@router.put("/{servico_id}", response_model=schemas.ServicoResponse)
def update_servico(
    servico_id: int,
    servico: schemas.ServicoCreate,
    db: Session = Depends(get_db)
):
    db_servico = db.query(models.Servico).filter(
        models.Servico.id == servico_id
    ).first()

    if not db_servico:
        return {"error": "Serviço não encontrado"}

    db_servico.nome = servico.nome
    db_servico.preco = servico.preco
    db_servico.duracao = servico.duracao

    db.commit()
    db.refresh(db_servico)

    return db_servico
