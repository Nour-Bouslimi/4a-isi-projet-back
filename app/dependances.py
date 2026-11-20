from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.database import get_session
from app.models import Role, Utilisateur
from app.security import decoder_token

# Indique à FastAPI  ou obtenir un token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/connexion")

# une session de base de données fournie par FastAPI
SessionDep = Annotated[Session, Depends(get_session)]


def utilisateur_connecte(session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]) -> Utilisateur:
    """Niveau 1 : le token est valide et l'utilisateur existe encore."""
    utilisateur_id = decoder_token(token)
    utilisateur = session.get(Utilisateur, utilisateur_id) if utilisateur_id else None
    if utilisateur is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return utilisateur


def utilisateur_actif(utilisateur: Annotated[Utilisateur, Depends(utilisateur_connecte)]) -> Utilisateur:
    """Niveau 2 : connecté ET non bloqué (vérifié à chaque requête)."""
    if utilisateur.bloque:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Compte bloqué")
    return utilisateur


def administrateur(utilisateur: Annotated[Utilisateur, Depends(utilisateur_actif)]) -> Utilisateur:
    """Niveau 3 : actif ET administrateur."""
    if utilisateur.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Réservé aux administrateurs")
    return utilisateur


# Raccourcis à utiliser dans les routes
UtilisateurConnecte = Annotated[Utilisateur, Depends(utilisateur_connecte)]
UtilisateurActif = Annotated[Utilisateur, Depends(utilisateur_actif)]
Administrateur = Annotated[Utilisateur, Depends(administrateur)]