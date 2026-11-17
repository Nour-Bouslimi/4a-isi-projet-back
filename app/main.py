from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables

# Fournit un contexte de durée de vie pour l'application FastAPI, permettant de créer la base de données et les tables au démarrage
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

# Crée l'application FastAPI avec le contexte de durée de vie défini
app = FastAPI(title="Pol-eat-heck API", version="0.1.0", lifespan=lifespan)

# Fournit un point de terminaison pour vérifier la version de l'API
@app.get("/api/", tags=["meta"])
def version():
    return {"version": app.version}