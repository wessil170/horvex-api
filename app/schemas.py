from pydantic import BaseModel, EmailStr, Field

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


class ClienteResponse(BaseModel):
    id: int
    salon_id: int
    nome: str
    telefone: str

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
    data: str
    horario: str
    status: str = "agendado"


class AgendamentoResponse(BaseModel):
    id: int
    salon_id: int
    cliente_id: int
    servico_id: int
    data: str
    horario: str
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
