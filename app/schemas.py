from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, time


class SalonCreate(BaseModel):
    nome: str
    slug: str


class SalonResponse(BaseModel):
    id: int
    nome: str
    slug: str
    plano: str

    class Config:
        from_attributes = True

class ClienteCreate(BaseModel):
    nome: str
    telefone: str
    observacoes: str | None = None

class ClienteResponse(BaseModel):
    id: int
    salon_id: int
    nome: str
    telefone: str
    observacoes: str | None
    class Config:
        from_attributes = True

class ServicoCreate(BaseModel):
    nome: str
    preco: float
    duracao: int


class ServicoResponse(BaseModel):
    id: int
    salon_id: int
    nome: str
    preco: float
    duracao: int

    class Config:
        from_attributes = True

class AgendamentoCreate(BaseModel):
    cliente_id: int
    servico_id: int
    profissional_id: int
    inicio: datetime

class AgendamentoResponse(BaseModel):
    id: int
    salon_id: int
    cliente_id: int
    servico_id: int
    profissional_id: int
    inicio: datetime
    fim: datetime
    status: str

    class Config:
        from_attributes = True

class RegisterRequest(BaseModel):
    salon_nome: str
    salon_slug: str
    nome: str
    email: EmailStr
    senha: str = Field(min_length=6, max_length=72)


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ProfissionalCreate(BaseModel):
    nome: str


class ProfissionalResponse(BaseModel):
    id: int
    salon_id: int
    nome: str

    class Config:
        from_attributes = True

class HorarioProfissionalCreate(BaseModel):
    dia_semana: int
    abertura: time
    fechamento: time


class HorarioProfissionalResponse(BaseModel):
    id: int
    profissional_id: int
    dia_semana: int
    abertura: time
    fechamento: time

    class Config:
        from_attributes = True


class AgendamentoPublicoCreate(BaseModel):
    nome: str
    telefone: str
    data: str
    horario: str
    servico_id: int
    profissional_id: int
    slug: str
