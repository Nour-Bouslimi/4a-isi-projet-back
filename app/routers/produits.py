from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.dependances import Administrateur, SessionDep
from app.models import Produit, ProduitBase
from app.schemas import StockModification

router = APIRouter(prefix="/produits", tags=["Produits"])


def produit_ou_404(session, produit_id: int) -> Produit:
    produit = session.get(Produit, produit_id)
    if produit is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Produit introuvable")
    return produit


#Public 

@router.get("", response_model=list[Produit], summary="Lister les produits")
def lister_produits(session: SessionDep, disponibles_seulement: bool = False):
    requete = select(Produit)
    if disponibles_seulement:
        requete = requete.where(Produit.disponible == True)  # noqa: E712
    return session.exec(requete).all()


@router.get("/{produit_id}", response_model=Produit, summary="Détail d'un produit")
def detail_produit(produit_id: int, session: SessionDep):
    return produit_ou_404(session, produit_id)


#Administrateur 

@router.post("", response_model=Produit, status_code=201, summary="Créer un produit (admin)")
def creer_produit(data: ProduitBase, admin: Administrateur, session: SessionDep):
    produit = Produit.model_validate(data)  # ProduitBase -> Produit (l'id sera généré)
    session.add(produit)
    session.commit()
    session.refresh(produit)
    return produit


@router.put("/{produit_id}", response_model=Produit, summary="Modifier un produit (admin)")
def modifier_produit(produit_id: int, data: ProduitBase, admin: Administrateur, session: SessionDep):
    produit = produit_ou_404(session, produit_id)
    produit.sqlmodel_update(data.model_dump())  # remplace tous les champs
    session.add(produit)
    session.commit()
    session.refresh(produit)
    return produit


@router.patch("/{produit_id}/stock", response_model=Produit, summary="Modifier stock / disponibilité (admin)")
def modifier_stock(produit_id: int, data: StockModification, admin: Administrateur, session: SessionDep):
    produit = produit_ou_404(session, produit_id)
    produit.stock = data.stock
    if data.disponible is not None:
        produit.disponible = data.disponible
    session.add(produit)
    session.commit()
    session.refresh(produit)
    return produit


@router.delete("/{produit_id}", status_code=204, summary="Supprimer un produit (admin)")
def supprimer_produit(produit_id: int, admin: Administrateur, session: SessionDep):
    produit = produit_ou_404(session, produit_id)
    session.delete(produit)
    try:
        session.commit()
    except IntegrityError:
        # Le produit apparaît dans une commande : la clé étrangère empêche sa suppression
        session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT,
                            "Produit déjà commandé : rendez-le indisponible plutôt que de le supprimer")