from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  
from app.database import create_db_and_tables
from app.routers import auth, commandes, fermetures, menus, produits, utilisateurs
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Pol-eat-heck API", version="0.1.0", lifespan=lifespan)

# Autorise le front (Live Server, port 5500) à appeler l'API pendant le développement
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Toutes les routes sont préfixées par /api
app.include_router(auth.router, prefix="/api")
app.include_router(utilisateurs.router, prefix="/api")
app.include_router(produits.router, prefix="/api")
app.include_router(fermetures.router, prefix="/api")
app.include_router(menus.router, prefix="/api")
app.include_router(commandes.router, prefix="/api")
@app.get("/api/", tags=["Meta"])
def version():
    return {"version": app.version}