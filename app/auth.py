from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database import get_db
from app import models


# ==========================================================
# CONFIGURAÇÕES JWT
# ==========================================================

SECRET_KEY = "supersecretkey"  # ⚠️ Colocar em variável de ambiente depois
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ==========================================================
# HASH DE SENHA (bcrypt puro)
# ==========================================================

def hash_senha(senha: str) -> str:
    senha_bytes = senha.encode("utf-8")
    hashed = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verificar_senha(senha: str, hash: str) -> bool:
    return bcrypt.checkpw(
        senha.encode("utf-8"),
        hash.encode("utf-8")
    )


# ==========================================================
# OAUTH2
# ==========================================================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ==========================================================
# CRIAÇÃO DE TOKEN
# ==========================================================

def criar_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ==========================================================
# USUÁRIO ATUAL (AUTENTICADO)
# ==========================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[str] = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()

    if user is None:
        raise credentials_exception

    return user


# ==========================================================
# SALÃO ATUAL (MULTI-TENANT REAL)
# ==========================================================

def get_current_salon(
    current_user: models.User = Depends(get_current_user)
) -> models.Salon:

    if current_user.salon is None:
        raise HTTPException(
            status_code=400,
            detail="Usuário não está vinculado a um salão"
        )

    return current_user.salon
