from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import get_current_salon

router = APIRouter(prefix="/profissionais", tags=["Profissionais"])


@router.post("/", response_model=schemas.ProfissionalResponse)
def criar_profissional(
    data: schemas.ProfissionalCreate,
    db: Session = Depends(get_db),
    salon: models.Salon = Depends(get_current_salon)
):
    novo = models.Profissional(
        nome=data.nome,
        salon_id=salon.id
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.get("/", response_model=list[schemas.ProfissionalResponse])
def listar_profissionais(
    db: Session = Depends(get_db),
    salon: models.Salon = Depends(get_current_salon)
):
    return db.query(models.Profissional).filter(
        models.Profissional.salon_id == salon.id
    ).all()


# ========================================
# LISTAR HORÁRIOS DO PROFISSIONAL
# ========================================

@router.get("/{profissional_id}/horarios", response_model=list[schemas.HorarioProfissionalResponse])
def listar_horarios(
    profissional_id: int,
    db: Session = Depends(get_db),
    salon: models.Salon = Depends(get_current_salon)
):

    profissional = db.query(models.Profissional).filter(
        models.Profissional.id == profissional_id,
        models.Profissional.salon_id == salon.id
    ).first()

    if not profissional:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")

    return profissional.horarios


# ========================================
# CRIAR HORÁRIO DO PROFISSIONAL
# ========================================

@router.post("/{profissional_id}/horarios", response_model=schemas.HorarioProfissionalResponse)
def criar_horario(
    profissional_id: int,
    data: schemas.HorarioProfissionalCreate,
    db: Session = Depends(get_db),
    salon: models.Salon = Depends(get_current_salon)
):

    profissional = db.query(models.Profissional).filter(
        models.Profissional.id == profissional_id,
        models.Profissional.salon_id == salon.id
    ).first()

    if not profissional:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")

    horario = models.HorarioProfissional(
        profissional_id=profissional_id,
        dia_semana=data.dia_semana,
        abertura=data.abertura,
        fechamento=data.fechamento
    )

    db.add(horario)
    db.commit()
    db.refresh(horario)

    return horario

@router.put("/{profissional_id}")
def atualizar_profissional(
    profissional_id: int,
    profissional: schemas.ProfissionalCreate,
    db: Session = Depends(get_db),
    current_salon = Depends(get_current_salon)
):

    p = db.query(models.Profissional).filter(
        models.Profissional.id == profissional_id,
        models.Profissional.salon_id == current_salon.id
    ).first()

    if not p:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")

    p.nome = profissional.nome

    db.commit()
    db.refresh(p)

    return p


@router.delete("/{profissional_id}")
def deletar_profissional(
    profissional_id: int,
    db: Session = Depends(get_db),
    current_salon = Depends(get_current_salon)
):

    p = db.query(models.Profissional).filter(
        models.Profissional.id == profissional_id,
        models.Profissional.salon_id == current_salon.id
    ).first()

    if not p:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")

    db.delete(p)
    db.commit()

    return {"mensagem":"Profissional deletado"}

@router.get("/salon/{salon_id}")
def get_profissionais_por_salao(salon_id: int, db: Session = Depends(get_db)):
    return db.query(models.Profissional)\
        .filter(models.Profissional.salon_id == salon_id)\
        .all()
@router.get("/publico/{salon_id}")
def listar_profissionais_publico(salon_id: int, db: Session = Depends(get_db)):
    profissionais = db.query(models.Profissional).filter(
        models.Profissional.salon_id == salon_id,
        models.Profissional.ativo == True
    ).all()

    return profissionais
