from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy import DateTime,Time
from datetime import datetime

class Salon(Base):
    __tablename__ = "salons"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    plano = Column(String, default="basic")

    users = relationship("User", back_populates="salon")
    clientes = relationship("Cliente", back_populates="salon")
    servicos = relationship("Servico", back_populates="salon")
    agendamentos = relationship("Agendamento", back_populates="salon")
    profissionais = relationship("Profissional", back_populates="salon")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha = Column(String, nullable=False)

    salon_id = Column(Integer, ForeignKey("salons.id"))

    salon = relationship("Salon", back_populates="users")


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    observacoes = Column(String, nullable=True)

    salon_id = Column(Integer, ForeignKey("salons.id"))

    salon = relationship("Salon", back_populates="clientes")
    agendamentos = relationship("Agendamento", back_populates="cliente")


class Servico(Base):
    __tablename__ = "servicos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    duracao = Column(Integer, nullable=False)

    salon_id = Column(Integer, ForeignKey("salons.id"))

    salon = relationship("Salon", back_populates="servicos")
    agendamentos = relationship("Agendamento", back_populates="servico")


class Agendamento(Base):
    __tablename__ = "agendamentos"

    id = Column(Integer, primary_key=True, index=True)

    inicio = Column(DateTime, nullable=False)
    fim = Column(DateTime, nullable=False)

    status = Column(String, default="agendado")

    salon_id = Column(Integer, ForeignKey("salons.id"))
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    servico_id = Column(Integer, ForeignKey("servicos.id"))
    profissional_id = Column(Integer, ForeignKey("profissionais.id"))

    salon = relationship("Salon", back_populates="agendamentos")
    cliente = relationship("Cliente", back_populates="agendamentos")
    servico = relationship("Servico", back_populates="agendamentos")
    profissional = relationship("Profissional", back_populates="agendamentos")

class Profissional(Base):
    __tablename__ = "profissionais"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    ativo = Column(Boolean, default=True)

    salon_id = Column(Integer, ForeignKey("salons.id"))

    salon = relationship("Salon", back_populates="profissionais")
    agendamentos = relationship("Agendamento", back_populates="profissional")
    horarios = relationship("HorarioProfissional", back_populates="profissional")
class HorarioProfissional(Base):
    __tablename__ = "horarios_profissional"

    id = Column(Integer, primary_key=True, index=True)

    profissional_id = Column(Integer, ForeignKey("profissionais.id"))
    dia_semana = Column(Integer, nullable=False)  # 0=segunda

    abertura = Column(Time, nullable=False)
    fechamento = Column(Time, nullable=False)

    profissional = relationship("Profissional", back_populates="horarios")
