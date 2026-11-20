from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from app.dependances import SessionDep
from app.models import Utilisateur
from app.schemas import Inscription, InscriptionReponse, Token
from app.security import creer_token, generer_mot_de_passe, hacher_mot_de_passe, verifier_mot_de_passe

router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post("/inscription", response_model=InscriptionReponse, status_code=201,
             summary="Créer un compte (le mot de passe est généré et affiché une seule fois)")
def inscription(data: Inscription, session: SessionDep):
    # 1. Le nom est-il déjà pris ?
    existant = session.exec(
        select(Utilisateur).where(Utilisateur.nom_utilisateur == data.nom_utilisateur)
    ).first()
    if existant:
        raise HTTPException(status.HTTP_409_CONFLICT, "Nom d'utilisateur déjà pris")

    # 2. Générer un mot de passe, stocker uniquement son hash (rôle 'standard' par défaut)
    mot_de_passe = generer_mot_de_passe()
    utilisateur = Utilisateur(
        nom_utilisateur=data.nom_utilisateur,
        mot_de_passe=hacher_mot_de_passe(mot_de_passe),
    )
    session.add(utilisateur)
    session.commit()

    # 3. Renvoyer le mot de passe en clair 
    return InscriptionReponse(nom_utilisateur=data.nom_utilisateur, mot_de_passe=mot_de_passe)


@router.post("/connexion", response_model=Token, summary="Se connecter et obtenir un token")
def connexion(form: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    utilisateur = session.exec(
        select(Utilisateur).where(Utilisateur.nom_utilisateur == form.username)
    ).first()
    # Même message que le nom ou le mot de passe soit faux : on ne révèle pas quels comptes existent
    if utilisateur is None or not verifier_mot_de_passe(form.password, utilisateur.mot_de_passe):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Identifiants incorrects")
    if utilisateur.bloque:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Compte bloqué")
    return Token(access_token=creer_token(utilisateur.id))