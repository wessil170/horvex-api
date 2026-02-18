from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.proxy_headers import ProxyHeadersMiddleware
from app.database import engine, Base
from app import models
from app.routes import salons, clientes, servicos, agendamentos, auth

app = FastAPI()

# =========================
# PROXY (OBRIGATÓRIO NO RAILWAY)
# =========================

app.add_middleware(
    ProxyHeadersMiddleware,
    trusted_hosts="*"
)

# =========================
# CORS (RAILWAY FRONTEND)
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://horvex-web-production.up.railway.app"
    ],
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

