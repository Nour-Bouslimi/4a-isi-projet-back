from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine

from app.config import DATABASE_URL

# Crée le moteur de base de données SQLite
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Activez les clés étrangères pour SQLite
@event.listens_for(engine, "connect")
def _enable_foreign_keys(dbapi_conn, _):
    dbapi_conn.execute("PRAGMA foreign_keys=ON")

# Crée la base de données et les tables si elles n'existent pas
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Fournit une session de base de données pour les opérations CRUD
def get_session():
    with Session(engine) as session:
        yield session