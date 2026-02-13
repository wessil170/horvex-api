from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import get_current_salon

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.get("/")
def listar_clientes(
    db: Session = Depends(get_db),
    current_salon = Depends(get_current_salon)
):
    return db.query(models.Cliente).filter(
        models.Cliente.salon_id == current_salon.id
    ).all()


@router.post("/")
def criar_cliente(
    cliente: schemas.ClienteCreate,
    db: Session = Depends(get_db),
    current_salon = Depends(get_current_salon)
):
    novo_cliente = models.Cliente(
        nome=cliente.nome,
        telefone=cliente.telefone,
        salon_id=current_salon.id
    )

    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)

    return novo_cliente
