from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth import hash_senha, verificar_senha, criar_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.TokenResponse)
def register(data: schemas.RegisterRequest, db: Session = Depends(get_db)):

    salon_existente = db.query(models.Salon).filter(
        models.Salon.slug == data.salon_slug
    ).first()

    if salon_existente:
        raise HTTPException(status_code=400, detail="Slug já existe")

    novo_salon = models.Salon(
        nome=data.salon_nome,
        slug=data.salon_slug
    )

    db.add(novo_salon)
    db.commit()
    db.refresh(novo_salon)

    novo_user = models.User(
        nome=data.nome,
        email=data.email,
        senha=hash_senha(data.senha),
        salon_id=novo_salon.id
    )

    db.add(novo_user)
    db.commit()
    db.refresh(novo_user)

    token = criar_token(novo_user.id)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.post("/login", response_model=schemas.TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(models.User).filter(
        models.User.email == form_data.username
    ).first()

    if not user:
        raise HTTPException(status_code=400, detail="Usuário não encontrado")

    if not verificar_senha(form_data.password, user.senha):
        raise HTTPException(status_code=400, detail="Senha incorreta")

    token = criar_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer"
    }
