from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app import models, schemas
from app.auth import hash_senha, criar_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.TokenResponse)
def register(data: schemas.RegisterRequest, db: Session = Depends(get_db)):

    try:
        # ===============================
        # 1️⃣ Verificar se slug já existe
        # ===============================
        salon_existente = db.query(models.Salon).filter(
            models.Salon.slug == data.salon_slug
        ).first()

        if salon_existente:
            raise HTTPException(
                status_code=400,
                detail="Slug já existe"
            )

        # ===============================
        # 2️⃣ Criar salão
        # ===============================
        novo_salon = models.Salon(
            nome=data.salon_nome,
            slug=data.salon_slug
        )

        db.add(novo_salon)
        db.commit()
        db.refresh(novo_salon)

        # ===============================
        # 3️⃣ Criar usuário
        # ===============================
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

        # ===============================
        # 4️⃣ Criar token
        # ===============================
        token = criar_token(novo_user.id)

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Email já está cadastrado"
        )

    except Exception as e:
        db.rollback()
        # 👇 AGORA MOSTRA ERRO REAL
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
