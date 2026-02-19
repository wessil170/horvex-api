from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app import models
from app.routes import salons, clientes, servicos, agendamentos, auth

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://horvex-web-production.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(salons.router)
app.include_router(clientes.router)
app.include_router(servicos.router)
app.include_router(agendamentos.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Horvex API running"}
