from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app import models
from app.routes import salons, clientes, servicos, agendamentos, auth

app = FastAPI()

# =========================
# CORS DEFINITIVO (produção inicial)
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # libera todas as origens (resolve problema da Vercel)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# DATABASE
# =========================

Base.metadata.create_all(bind=engine)

# =========================
# ROTAS
# =========================

app.include_router(salons.router)
app.include_router(clientes.router)
app.include_router(servicos.router)
app.include_router(agendamentos.router)
app.include_router(auth.router)

# =========================
# ROOT
# =========================

@app.get("/")
def root():
    return {"message": "Horvex API running"}
