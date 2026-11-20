
import sys

from sqlmodel import Session, select

from app.database import create_db_and_tables, engine
from app.models import Role, Utilisateur
from app.security import hacher_mot_de_passe

if len(sys.argv) != 3:
    sys.exit("Usage : python create_admin.py <nom_utilisateur> <mot_de_passe>")

nom, mot_de_passe = sys.argv[1], sys.argv[2]
create_db_and_tables()

with Session(engine) as session:
    if session.exec(select(Utilisateur).where(Utilisateur.nom_utilisateur == nom)).first():
        sys.exit(f"Erreur : '{nom}' existe déjà")
    session.add(Utilisateur(nom_utilisateur=nom, mot_de_passe=hacher_mot_de_passe(mot_de_passe), role=Role.admin))
    session.commit()

print(f"Administrateur '{nom}' créé.")