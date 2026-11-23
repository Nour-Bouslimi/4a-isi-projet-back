from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.dependances import Administrateur, SessionDep
from app.models import Menu, Produit
from app.schemas import MenuCreation, MenuDisponibilite, MenuReponse

router = APIRouter(prefix="/menus", tags=["Menus"])


def menu_ou_404(session, menu_id: int) -> Menu:
    menu = session.get(Menu, menu_id)
    if menu is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Menu introuvable")
    return menu


def menu_disponible(menu: Menu, jour: date) -> bool:
    """Un menu est disponible un jour donné si ce jour est dans [date_debut, date_fin].
    Une date vide = pas de limite de ce côté (deux dates vides = menu permanent).
    Réutilisée par les commandes (étape 8.6)."""
    if menu.date_debut and jour < menu.date_debut:
        return False
    if menu.date_fin and jour > menu.date_fin:
        return False
    return True


#public

@router.get("", response_model=list[MenuReponse], summary="Lister les menus (filtre optionnel par jour)")
def lister_menus(session: SessionDep, jour: Optional[date] = None):
    menus = session.exec(select(Menu)).all()
    if jour:
        menus = [m for m in menus if menu_disponible(m, jour)]
    return menus


@router.get("/{menu_id}", response_model=MenuReponse, summary="Détail d'un menu")
def detail_menu(menu_id: int, session: SessionDep):
    return menu_ou_404(session, menu_id)


#  Administrateur

@router.post("", response_model=MenuReponse, status_code=201, summary="Créer un menu (admin)")
def creer_menu(data: MenuCreation, admin: Administrateur, session: SessionDep):
    # Récupérer les produits demandés et vérifier qu'ils existent tous
    ids = set(data.produit_ids)
    produits = session.exec(select(Produit).where(Produit.id.in_(ids))).all() if ids else []
    if len(produits) != len(ids):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Un ou plusieurs produits n'existent pas")

    menu = Menu(**data.model_dump(exclude={"produit_ids"}), produits=produits)
    session.add(menu)  # SQLModel remplit aussi la table menu_produit
    session.commit()
    session.refresh(menu)
    return menu


@router.patch("/{menu_id}/disponibilite", response_model=MenuReponse,
              summary="Modifier les dates de disponibilité (admin)")
def modifier_disponibilite(menu_id: int, data: MenuDisponibilite, admin: Administrateur, session: SessionDep):
    menu = menu_ou_404(session, menu_id)
    menu.date_debut = data.date_debut
    menu.date_fin = data.date_fin
    session.add(menu)
    session.commit()
    session.refresh(menu)
    return menu


@router.delete("/{menu_id}", status_code=204, summary="Supprimer un menu (admin)")
def supprimer_menu(menu_id: int, admin: Administrateur, session: SessionDep):
    menu = menu_ou_404(session, menu_id)
    session.delete(menu)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT,
                            "Menu déjà commandé : modifiez ses dates plutôt que de le supprimer")