from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth import get_current_salon

router = APIRouter(prefix="/agendamentos", tags=["Agendamentos"])


@router.post("/", response_model=schemas.AgendamentoResponse)
def create_agendamento(
    agendamento: schemas.AgendamentoCreate,
    db: Session = Depends(get_db),
    current_salon = Depends(get_current_salon)
):
    # 🔐 Verificar se cliente pertence ao salão
    cliente = db.query(models.Cliente).filter(
        models.Cliente.id == agendamento.cliente_id,
        models.Cliente.salon_id == current_salon.id
    ).first()

    if not cliente:
        raise HTTPException(status_code=400, detail="Cliente inválido")

    # 🔐 Verificar se serviço pertence ao salão
    servico = db.query(models.Servico).filter(
        models.Servico.id == agendamento.servico_id,
        models.Servico.salon_id == current_salon.id
    ).first()

    if not servico:
        raise HTTPException(status_code=400, detail="Serviço inválido")

    novo_agendamento = models.Agendamento(
        salon_id=current_salon.id,
        cliente_id=agendamento.cliente_id,
        servico_id=agendamento.servico_id,
        data=agendamento.data,
        horario=agendamento.horario,
        status=agendamento.status,
    )

    db.add(novo_agendamento)
    db.commit()
    db.refresh(novo_agendamento)

    return novo_agendamento


@router.get("/", response_model=list[schemas.AgendamentoResponse])
def list_agendamentos(
    db: Session = Depends(get_db),
    current_salon = Depends(get_current_salon)
):
    return db.query(models.Agendamento).filter(
        models.Agendamento.salon_id == current_salon.id
    ).all()


@router.put("/{agendamento_id}", response_model=schemas.AgendamentoResponse)
def update_agendamento_status(
    agendamento_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_salon = Depends(get_current_salon)
):
    agendamento = db.query(models.Agendamento).filter(
        models.Agendamento.id == agendamento_id,
        models.Agendamento.salon_id == current_salon.id
    ).first()

    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")

    agendamento.status = status
    db.commit()
    db.refresh(agendamento)

    return agendamento


@router.put("/editar/{agendamento_id}", response_model=schemas.AgendamentoResponse)
def editar_agendamento(
    agendamento_id: int,
    agendamento: schemas.AgendamentoCreate,
    db: Session = Depends(get_db),
    current_salon = Depends(get_current_salon)
):
    db_agendamento = db.query(models.Agendamento).filter(
        models.Agendamento.id == agendamento_id,
        models.Agendamento.salon_id == current_salon.id
    ).first()

    if not db_agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")

    # 🔐 Validar novamente cliente e serviço
    cliente = db.query(models.Cliente).filter(
        models.Cliente.id == agendamento.cliente_id,
        models.Cliente.salon_id == current_salon.id
    ).first()

    if not cliente:
        raise HTTPException(status_code=400, detail="Cliente inválido")

    servico = db.query(models.Servico).filter(
        models.Servico.id == agendamento.servico_id,
        models.Servico.salon_id == current_salon.id
    ).first()

    if not servico:
        raise HTTPException(status_code=400, detail="Serviço inválido")

    db_agendamento.cliente_id = agendamento.cliente_id
    db_agendamento.servico_id = agendamento.servico_id
    db_agendamento.data = agendamento.data
    db_agendamento.horario = agendamento.horario

    db.commit()
    db.refresh(db_agendamento)

    return db_agendamento
