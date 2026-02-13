from pydantic import BaseModel, EmailStr
from typing import Optional


# =============================
# CLIENTE
# =============================

class ClienteCreate(BaseModel):
    nome: str
    telefone: str


class ClienteResponse(BaseModel):
    id: int
    nome: str
    telefone: str

    class Config:
        from_attributes = True


# =============================
# SERVIÇO
# =============================

class ServicoCreate(BaseModel):
    nome: str
    preco: float
    duracao: int


class ServicoResponse(BaseModel):
    id: int
    nome: str
    preco: float
    duracao: int

    class Config:
        from_attributes = True


# =============================
# AGENDAMENTO
# =============================

class AgendamentoCreate(BaseModel):
    cliente_id: int
    servico_id: int
    data: str
    horario: str


class AgendamentoResponse(BaseModel):
    id: int
    data: str
    horario: str
    status: str

    class Config:
        from_attributes = True


# =============================
# AUTH
# =============================

class RegisterRequest(BaseModel):
    salon_nome: str
    salon_slug: str
    nome: str
    email: EmailStr
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: Optional[str] = "bearer"
