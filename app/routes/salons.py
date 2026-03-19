from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas

router = APIRouter(prefix="/salons", tags=["Salons"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.SalonResponse)
def create_salon(salon: schemas.SalonCreate, db: Session = Depends(get_db)):
    db_salon = models.Salon(
        nome=salon.nome,
        slug=salon.slug,
    )
    db.add(db_salon)
    db.commit()
    db.refresh(db_salon)
    return db_salon

# 🔎 Buscar salão por SLUG (ESSENCIAL)
@router.get("/slug/{slug}", response_model=schemas.SalonResponse)
def get_salon_by_slug(slug: str, db: Session = Depends(get_db)):
    salon = db.query(models.Salon).filter(models.Salon.slug == slug).first()

    if not salon:
        raise HTTPException(status_code=404, detail="Salão não encontrado")

    return salon


# 📋 Listar salões (opcional, mas útil)
@router.get("/", response_model=list[schemas.SalonResponse])
def list_salons(db: Session = Depends(get_db)):
    return db.query(models.Salon).all()
