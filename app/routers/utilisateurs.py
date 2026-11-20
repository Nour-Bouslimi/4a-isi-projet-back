from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.dependances import Administrateur, SessionDep, UtilisateurConnecte
from app.models import Utilisateur
from app.schemas import Blocage, ChangementMotDePasse, UtilisateurReponse
from app.security import hacher_mot_de_passe, verifier_mot_de_passe

router = APIRouter(prefix="/utilisateurs", tags=["Utilisateurs"])


# Utilisateur connecté

@router.get("/me", response_model=UtilisateurReponse, summary="Mon profil")
def mon_profil(utilisateur: UtilisateurConnecte):
    return utilisateur


@router.patch("/me/mot-de-passe", status_code=204, summary="Changer mon mot de passe")
def changer_mot_de_passe(data: ChangementMotDePasse, utilisateur: UtilisateurConnecte, session: SessionDep):
    if not verifier_mot_de_passe(data.ancien_mot_de_passe, utilisateur.mot_de_passe):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Ancien mot de passe incorrect")
    utilisateur.mot_de_passe = hacher_mot_de_passe(data.nouveau_mot_de_passe)
    session.add(utilisateur)
    session.commit()


# Administrateur 

@router.get("", response_model=list[UtilisateurReponse], summary="Lister les utilisateurs (admin)")
def lister_utilisateurs(admin: Administrateur, session: SessionDep):
    return session.exec(select(Utilisateur)).all()


@router.patch("/{utilisateur_id}/blocage", response_model=UtilisateurReponse,
              summary="Bloquer / débloquer un utilisateur (admin)")
def bloquer_utilisateur(utilisateur_id: int, data: Blocage, admin: Administrateur, session: SessionDep):
    utilisateur = session.get(Utilisateur, utilisateur_id)
    if utilisateur is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Utilisateur introuvable")
    if utilisateur.id == admin.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Impossible de se bloquer soi-même")
    utilisateur.bloque = data.bloque
    session.add(utilisateur)
    session.commit()
    session.refresh(utilisateur)
    return utilisateur