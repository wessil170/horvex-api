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
        observacoes=cliente.observacoes,
        salon_id=current_salon.id
    )

    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)

    return novo_cliente

@router.put("/{cliente_id}")
def atualizar_cliente(
    cliente_id: int,
    cliente: schemas.ClienteCreate,
    db: Session = Depends(get_db),
    current_salon = Depends(get_current_salon)
):

    db_cliente = db.query(models.Cliente).filter(
        models.Cliente.id == cliente_id,
        models.Cliente.salon_id == current_salon.id
    ).first()

    if not db_cliente:
        return {"erro": "Cliente não encontrado"}

    db_cliente.nome = cliente.nome
    db_cliente.telefone = cliente.telefone
    db_cliente.observacoes = cliente.observacoes

    db.commit()
    db.refresh(db_cliente)

    return db_cliente

@router.put("/{cliente_id}", response_model=schemas.ClienteResponse)
def atualizar_cliente(
    cliente_id: int,
    cliente: schemas.ClienteCreate,
    db: Session = Depends(get_db),
    current_salon = Depends(get_current_salon)
):

    db_cliente = db.query(models.Cliente).filter(
        models.Cliente.id == cliente_id,
        models.Cliente.salon_id == current_salon.id
    ).first()

    if not db_cliente:
        return {"erro": "Cliente não encontrado"}

    db_cliente.nome = cliente.nome
    db_cliente.telefone = cliente.telefone
    db_cliente.observacoes = cliente.observacoes

    db.commit()
    db.refresh(db_cliente)

    return db_cliente
@router.delete("/{cliente_id}")
def deletar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_salon = Depends(get_current_salon)
):

    cliente = db.query(models.Cliente).filter(
        models.Cliente.id == cliente_id,
        models.Cliente.salon_id == current_salon.id
    ).first()

    if not cliente:
        return {"erro": "Cliente não encontrado"}

    db.delete(cliente)
    db.commit()

    return {"mensagem": "Cliente deletado"}
