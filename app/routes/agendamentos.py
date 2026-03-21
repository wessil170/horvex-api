from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app import models, schemas
from app.auth import get_current_salon
from app.schemas import AgendamentoPublicoCreate

router = APIRouter(prefix="/agendamentos", tags=["Agendamentos"])


# =========================================
# CRIAR AGENDAMENTO (COM BLOQUEIO INTELIGENTE)
# =========================================

@router.post("/", response_model=schemas.AgendamentoResponse)
def criar_agendamento(
    data: schemas.AgendamentoCreate,
    db: Session = Depends(get_db),
    salon: models.Salon = Depends(get_current_salon)
):

    # Buscar serviço para saber duração
    servico = db.query(models.Servico).filter(
        models.Servico.id == data.servico_id,
        models.Servico.salon_id == salon.id
    ).first()

    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    inicio = data.inicio
    fim = inicio + timedelta(minutes=servico.duracao)

    # Verificar conflito
    conflito = db.query(models.Agendamento).filter(
        models.Agendamento.salon_id == salon.id,
        models.Agendamento.profissional_id == data.profissional_id,
        models.Agendamento.status != "cancelado",
        models.Agendamento.inicio < fim,
        models.Agendamento.fim > inicio
    ).first()

    if conflito:
        raise HTTPException(
            status_code=400,
            detail="Horário conflita com outro agendamento"
        )

    novo = models.Agendamento(
        inicio=inicio,
        fim=fim,
        salon_id=salon.id,
        cliente_id=data.cliente_id,
        servico_id=data.servico_id,
        profissional_id=data.profissional_id
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)

    return novo


# =========================================
# LISTAR AGENDAMENTOS DO SALÃO
# =========================================

@router.get("/")
def listar_agendamentos(
    db: Session = Depends(get_db),
    salon: models.Salon = Depends(get_current_salon)
):
    agendamentos = db.query(models.Agendamento).filter(
        models.Agendamento.salon_id == salon.id
    ).all()

    resultado = []

    for ag in agendamentos:
        resultado.append({
            "id": ag.id,
            "inicio": ag.inicio,
            "fim": ag.fim,
            "cliente": ag.cliente.nome if ag.cliente else None,
            "servico": ag.servico.nome if ag.servico else None,
            "profissional": ag.profissional.nome if ag.profissional else None
        })

    return resultado


@router.get("/dia/{data}")
def agenda_por_dia(
    data: str,
    db: Session = Depends(get_db),
    salon: models.Salon = Depends(get_current_salon)
):

    try:
        data_inicio = datetime.strptime(data, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD")

    data_fim = data_inicio + timedelta(days=1)

    agendamentos = db.query(models.Agendamento).filter(
        models.Agendamento.salon_id == salon.id,
        models.Agendamento.inicio >= data_inicio,
        models.Agendamento.inicio < data_fim
    ).all()

    return agendamentos

@router.get("/agenda-profissionais/{data}")
def agenda_por_profissional(
    data: str,
    db: Session = Depends(get_db),
    salon: models.Salon = Depends(get_current_salon)
):
    try:
        data_inicio = datetime.strptime(data, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de data inválido")

    data_fim = data_inicio + timedelta(days=1)

    agendamentos = db.query(models.Agendamento).filter(
        models.Agendamento.salon_id == salon.id,
        models.Agendamento.inicio >= data_inicio,
        models.Agendamento.inicio < data_fim
    ).all()

    profissionais = db.query(models.Profissional).filter(
        models.Profissional.salon_id == salon.id,
        models.Profissional.ativo == True
    ).all()

    agenda = {}

    for prof in profissionais:
        agenda[prof.nome] = []

    for ag in agendamentos:
        prof_nome = ag.profissional.nome

        agenda[prof_nome].append({
            "inicio": ag.inicio.strftime("%H:%M"),
            "fim": ag.fim.strftime("%H:%M"),
            "cliente": ag.cliente.nome,
            "servico": ag.servico.nome
        })

    return agenda

@router.get("/horarios-disponiveis")
def horarios_disponiveis(
    data: str,
    profissional_id: int,
    servico_id: int,
    slug: str,
    db: Session = Depends(get_db),


):

    salon = db.query(models.Salon).filter(
       models.Salon.slug == slug
    ).first()

    if not salon:
       raise HTTPException(status_code=404, detail="Salão não encontrado")


    data_inicio = datetime.strptime(data, "%Y-%m-%d")
    data_fim = data_inicio + timedelta(days=1)

    servico = db.query(models.Servico).filter(
        models.Servico.id == servico_id,
        models.Servico.salon_id == salon.id
    ).first()

    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    duracao = servico.duracao

    # descobrir dia da semana
    dia_semana = data_inicio.weekday()

    horario_prof = db.query(models.HorarioProfissional).filter(
        models.HorarioProfissional.profissional_id == profissional_id,
        models.HorarioProfissional.dia_semana == dia_semana
    ).first()

    # definir horário de trabalho
    if horario_prof:
        abertura = datetime.combine(data_inicio.date(), horario_prof.abertura)
        fechamento = datetime.combine(data_inicio.date(), horario_prof.fechamento)
    else:
        abertura = datetime.combine(data_inicio.date(), datetime.strptime("09:00", "%H:%M").time())
        fechamento = datetime.combine(data_inicio.date(), datetime.strptime("18:00", "%H:%M").time())

    # buscar agendamentos do profissional no dia
    agendamentos = db.query(models.Agendamento).filter(
        models.Agendamento.profissional_id == profissional_id,
        models.Agendamento.salon_id == salon.id,
        models.Agendamento.inicio >= data_inicio,
        models.Agendamento.inicio < data_fim
    ).all()

    horarios_disponiveis = []

    horario_atual = abertura

    while horario_atual + timedelta(minutes=duracao) <= fechamento:

        inicio = horario_atual
        fim = inicio + timedelta(minutes=duracao)

        conflito = False

        for ag in agendamentos:
            if inicio < ag.fim and fim > ag.inicio:
                conflito = True
                break

        if not conflito:
            horarios_disponiveis.append(inicio.strftime("%H:%M"))

        horario_atual += timedelta(minutes=30)

    return horarios_disponiveis
@router.get("/agenda/{data}")
def agenda_do_dia(
    data: str,
    db: Session = Depends(get_db),
    salon: models.Salon = Depends(get_current_salon)
):

    data_inicio = datetime.strptime(data, "%Y-%m-%d")
    data_fim = data_inicio + timedelta(days=1)

    profissionais = db.query(models.Profissional).filter(
        models.Profissional.salon_id == salon.id,
        models.Profissional.ativo == True
    ).all()

    resultado = {}

    for prof in profissionais:

        agendamentos = db.query(models.Agendamento).filter(
            models.Agendamento.profissional_id == prof.id,
            models.Agendamento.salon_id == salon.id,
            models.Agendamento.inicio >= data_inicio,
            models.Agendamento.inicio < data_fim
        ).all()

        lista = []

        for ag in agendamentos:

            cliente_nome = ag.cliente.nome if ag.cliente else None
            servico_nome = ag.servico.nome if ag.servico else None

            lista.append({
                "inicio": ag.inicio.strftime("%H:%M"),
                "fim": ag.fim.strftime("%H:%M"),
                "cliente": cliente_nome,
                "servico": servico_nome
            })

        resultado[prof.nome] = lista

    return resultado
@router.put("/{agendamento_id}")
def editar_agendamento(
    agendamento_id: int,
    dados: schemas.AgendamentoCreate,
    db: Session = Depends(get_db),
    current_salon = Depends(get_current_salon)
):

    agendamento = db.query(models.Agendamento).filter(
        models.Agendamento.id == agendamento_id,
        models.Agendamento.salon_id == current_salon.id
    ).first()

    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")

    agendamento.cliente_id = dados.cliente_id
    agendamento.servico_id = dados.servico_id
    agendamento.profissional_id = dados.profissional_id
    agendamento.inicio = dados.inicio

    servico = db.query(models.Servico).filter(
        models.Servico.id == dados.servico_id
    ).first()

    agendamento.fim = dados.inicio + timedelta(minutes=servico.duracao)

    db.commit()
    db.refresh(agendamento)

    return agendamento

@router.delete("/{agendamento_id}")
def excluir_agendamento(
    agendamento_id: int,
    db: Session = Depends(get_db),
    current_salon = Depends(get_current_salon)
):

    agendamento = db.query(models.Agendamento).filter(
        models.Agendamento.id == agendamento_id,
        models.Agendamento.salon_id == current_salon.id
    ).first()

    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")

    db.delete(agendamento)
    db.commit()

    return {"message": "Agendamento removido"}

@router.post("/publico")
def criar_agendamento_publico(
    dados: AgendamentoPublicoCreate,
    db: Session = Depends(get_db),
):
    
    # 🔍 buscar salão
    salon = db.query(models.Salon).filter(
        models.Salon.slug == dados.slug
    ).first()

    if not salon:
        raise HTTPException(status_code=404, detail="Salão não encontrado")

    # 🔍 buscar serviço
    servico = db.query(models.Servico).filter(
        models.Servico.id == dados.servico_id,
        models.Servico.salon_id == salon.id
    ).first()

    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    # 🔍 criar ou buscar cliente
    cliente = db.query(models.Cliente).filter(
        models.Cliente.telefone == dados.telefone,
        models.Cliente.salon_id == salon.id
    ).first()

    if not cliente:
        cliente = models.Cliente(
            nome=dados.nome,
            telefone=dados.telefone,
            salon_id=salon.id
        )
        db.add(cliente)
        db.commit()
        db.refresh(cliente)

    # 🕐 montar datas
    inicio = datetime.strptime(f"{dados.data} {dados.horario}", "%Y-%m-%d %H:%M")
    fim = inicio + timedelta(minutes=servico.duracao)

    # 🚫 validar conflito
    conflito = db.query(models.Agendamento).filter(
        models.Agendamento.profissional_id == dados.profissional_id,
        models.Agendamento.salon_id == salon.id,
        models.Agendamento.inicio < fim,
        models.Agendamento.fim > inicio
    ).first()

    if conflito:
        raise HTTPException(status_code=400, detail="Horário já ocupado")

    # 💾 salvar agendamento
    novo = models.Agendamento(
        inicio=inicio,
        fim=fim,
        status="agendado",
        salon_id=salon.id,
        cliente_id=cliente.id,
        servico_id=dados.servico_id,
        profissional_id=dados.profissional_id
    )

    db.add(novo)
    db.commit()

    return {"message": "Agendamento criado com sucesso"}
