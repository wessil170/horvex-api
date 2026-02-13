from fastapi import APIRouter, Depends
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
