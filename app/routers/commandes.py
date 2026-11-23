from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.dependances import Administrateur, SessionDep, UtilisateurActif, UtilisateurConnecte
from app.models import Commande, Fermeture, LigneCommande, Menu, Produit
from app.routers.menus import menu_disponible
from app.schemas import CommandeCreation, CommandeReponse, LigneCommandeReponse, StatutModification

router = APIRouter(prefix="/commandes", tags=["Commandes"])


def erreur(message: str):
    raise HTTPException(status.HTTP_400_BAD_REQUEST, message)


def vers_reponse(session, commande: Commande) -> CommandeReponse:
    """Construit la réponse en ajoutant le total (calculé, jamais stocké)."""
    total = 0.0
    for ligne in commande.lignes:
        article = session.get(Produit, ligne.produit_id) if ligne.produit_id else session.get(Menu, ligne.menu_id)
        total += article.prix * ligne.quantite
    return CommandeReponse(
        id=commande.id,
        utilisateur_id=commande.utilisateur_id,
        date_commande=commande.date_commande,
        date_retrait=commande.date_retrait,
        statut=commande.statut,
        lignes=[LigneCommandeReponse.model_validate(l) for l in commande.lignes],
        total=round(total, 2),
    )


#  Utilisateur

@router.post("", response_model=CommandeReponse, status_code=201, summary="Passer une commande")
def creer_commande(data: CommandeCreation, utilisateur: UtilisateurActif, session: SessionDep):
    # Règle 1 : la date de retrait n'est pas dans le passé
    if data.date_retrait < date.today():
        erreur("La date de retrait est dans le passé")

    # Règle 2 : l'établissement n'est pas fermé ce jour-là
    fermeture = session.exec(
        select(Fermeture).where(Fermeture.date_fermeture == data.date_retrait)
    ).first()
    if fermeture:
        erreur("L'établissement est fermé ce jour-là")

    commande = Commande(utilisateur_id=utilisateur.id, date_retrait=data.date_retrait)

    for ligne in data.lignes:
        if ligne.produit_id is not None:
            produit = session.get(Produit, ligne.produit_id)
            # Règle 3 : le produit existe et est disponible
            if produit is None or not produit.disponible:
                erreur(f"Produit {ligne.produit_id} indisponible")
            # Règle 4 : stock suffisant -> on le décrémente
            if produit.stock < ligne.quantite:
                erreur(f"Stock insuffisant pour « {produit.nom} » (reste {produit.stock})")
            produit.stock -= ligne.quantite
            session.add(produit)
        else:
            menu = session.get(Menu, ligne.menu_id)
            # Règle 5 : le menu existe et est disponible à la date de retrait
            if menu is None or not menu_disponible(menu, data.date_retrait):
                erreur(f"Menu {ligne.menu_id} indisponible à cette date")

        commande.lignes.append(LigneCommande(**ligne.model_dump()))

    session.add(commande)
    session.commit() 
    session.refresh(commande)
    return vers_reponse(session, commande)


@router.get("/me", response_model=list[CommandeReponse], summary="Mes commandes")
def mes_commandes(utilisateur: UtilisateurConnecte, session: SessionDep):
    commandes = session.exec(
        select(Commande).where(Commande.utilisateur_id == utilisateur.id)
        .order_by(Commande.date_retrait.desc())
    ).all()
    return [vers_reponse(session, c) for c in commandes]


#  Administrateur 

@router.get("", response_model=list[CommandeReponse], summary="Lister les commandes (admin)")
def lister_commandes(admin: Administrateur, session: SessionDep, jour: Optional[date] = None):
    requete = select(Commande).order_by(Commande.date_retrait)
    if jour:
        requete = requete.where(Commande.date_retrait == jour)
    return [vers_reponse(session, c) for c in session.exec(requete).all()]


@router.patch("/{commande_id}/statut", response_model=CommandeReponse,
              summary="Changer le statut d'une commande (admin)")
def modifier_statut(commande_id: int, data: StatutModification, admin: Administrateur, session: SessionDep):
    commande = session.get(Commande, commande_id)
    if commande is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Commande introuvable")
    commande.statut = data.statut
    session.add(commande)
    session.commit()
    session.refresh(commande)
    return vers_reponse(session, commande)