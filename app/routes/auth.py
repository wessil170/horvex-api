from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app import models, schemas
from app.auth import hash_senha, verificar_senha, criar_token

router = APIRouter(prefix="/auth", tags=["auth"])


# ==========================================================
# REGISTER
# ==========================================================

@router.post("/register", response_model=schemas.TokenResponse)
def register(data: schemas.RegisterRequest, db: Session = Depends(get_db)):
    try:
        # Verificar slug
        salon_existente = db.query(models.Salon).filter(
            models.Salon.slug == data.salon_slug
        ).first()

        if salon_existente:
            raise HTTPException(status_code=400, detail="Slug já existe")

        # Criar salão
        novo_salon = models.Salon(
            nome=data.salon_nome,
            slug=data.salon_slug
        )

        db.add(novo_salon)
        db.commit()
        db.refresh(novo_salon)

        # Criar usuário
        senha_hash = hash_senha(data.senha)

        novo_user = models.User(
            nome=data.nome,
            email=data.email,
            senha=senha_hash,
            salon_id=novo_salon.id
        )

        db.add(novo_user)
        db.commit()
        db.refresh(novo_user)

        # Criar token
        token = criar_token(novo_user.id)

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email já está cadastrado")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# LOGIN
# ==========================================================

@router.post("/login", response_model=schemas.TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.email == form_data.username
    ).first()

    if not user:
        raise HTTPException(status_code=400, detail="Credenciais inválidas")

    if not verificar_senha(form_data.password, user.senha):
        raise HTTPException(status_code=400, detail="Credenciais inválidas")

    token = criar_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer"
    }
