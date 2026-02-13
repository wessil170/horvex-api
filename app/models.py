from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


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
    data = Column(String, nullable=False)
    horario = Column(String, nullable=False)
    status = Column(String, default="agendado")

    salon_id = Column(Integer, ForeignKey("salons.id"))
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    servico_id = Column(Integer, ForeignKey("servicos.id"))

    salon = relationship("Salon", back_populates="agendamentos")
    cliente = relationship("Cliente", back_populates="agendamentos")
    servico = relationship("Servico", back_populates="agendamentos")
