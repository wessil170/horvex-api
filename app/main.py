from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app import models
from app.routes import salons, clientes, servicos, agendamentos, auth

app = FastAPI()

# =========================
# CORS CONFIGURAÇÃO
# =========================

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://horvex-web.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Permite qualquer preview da Vercel
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
