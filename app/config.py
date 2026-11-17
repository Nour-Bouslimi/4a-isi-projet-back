import os

# Chemin de la base SQLite (fichier créé automatiquement à la racine du projet)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./poleatheck.db")

# Clé secrète pour signer les tokens JWT (à changer en production)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-change-me-in-production-please")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60