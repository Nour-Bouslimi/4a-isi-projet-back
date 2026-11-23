from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.dependances import Administrateur, SessionDep
from app.models import Fermeture, FermetureBase

router = APIRouter(prefix="/fermetures", tags=["Fermetures"])


@router.get("", response_model=list[Fermeture], summary="Lister les jours de fermeture")
def lister_fermetures(session: SessionDep):
    return session.exec(select(Fermeture).order_by(Fermeture.date_fermeture)).all()


@router.post("", response_model=Fermeture, status_code=201, summary="Ajouter un jour de fermeture (admin)")
def creer_fermeture(data: FermetureBase, admin: Administrateur, session: SessionDep):
    existante = session.exec(
        select(Fermeture).where(Fermeture.date_fermeture == data.date_fermeture)
    ).first()
    if existante:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ce jour est déjà fermé")
    fermeture = Fermeture.model_validate(data)
    session.add(fermeture)
    session.commit()
    session.refresh(fermeture)
    return fermeture


@router.delete("/{fermeture_id}", status_code=204, summary="Supprimer un jour de fermeture (admin)")
def supprimer_fermeture(fermeture_id: int, admin: Administrateur, session: SessionDep):
    fermeture = session.get(Fermeture, fermeture_id)
    if fermeture is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Fermeture introuvable")
    session.delete(fermeture)
    session.commit()