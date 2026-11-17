from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


# ---------- Enumérations ----------
class Role(str, Enum):
    standard = "standard"
    admin = "admin"


class Statut(str, Enum):
    en_attente = "en_attente"
    recuperee = "recuperee"
    annulee = "annulee"
    non_honoree = "non_honoree"


# ---------- Tables  ----------

class Utilisateur(SQLModel, table=True):
    __tablename__ = "utilisateur"

    id: Optional[int] = Field(default=None, primary_key=True)
    nom_utilisateur: str = Field(unique=True, index=True)
    mot_de_passe: str  
    role: Role = Role.standard
    bloque: bool = False

    commandes: list["Commande"] = Relationship(back_populates="utilisateur")


class MenuProduit(SQLModel, table=True):
    __tablename__ = "menu_produit"

    menu_id: int = Field(foreign_key="menu.id", primary_key=True, ondelete="CASCADE")
    produit_id: int = Field(foreign_key="produit.id", primary_key=True, ondelete="CASCADE")

# cette classe est utilisée pour la relation many-to-many entre Menu et Produit
class ProduitBase(SQLModel):
    """Champs d'un produit, SANS id : sert aussi de données d'entrée de l'API."""
    nom: str = Field(min_length=1)
    description: Optional[str] = None
    prix: float = Field(ge=0)
    stock: int = Field(default=0, ge=0)
    disponible: bool = True

# cette classe est héritée par Produit, qui ajoute l'id et la relation avec Menu
class Produit(ProduitBase, table=True):
    __tablename__ = "produit"

    id: Optional[int] = Field(default=None, primary_key=True)

    menus: list["Menu"] = Relationship(back_populates="produits", link_model=MenuProduit)

class Menu(SQLModel, table=True):
    __tablename__ = "menu"

    id: Optional[int] = Field(default=None, primary_key=True)
    nom: str
    description: Optional[str] = None
    prix: float = Field(ge=0)
    date_debut: Optional[date] = None  # NULL = menu permanent
    date_fin: Optional[date] = None

    produits: list[Produit] = Relationship(back_populates="menus", link_model=MenuProduit)


class FermetureBase(SQLModel):
    """Champs d'une fermeture, SANS id : sert aussi de données d'entrée de l'API."""
    date_fermeture: date = Field(unique=True)
    motif: Optional[str] = None


class Fermeture(FermetureBase, table=True):
    __tablename__ = "fermeture"

    id: Optional[int] = Field(default=None, primary_key=True)

class Commande(SQLModel, table=True):
    __tablename__ = "commande"

    id: Optional[int] = Field(default=None, primary_key=True)
    utilisateur_id: int = Field(foreign_key="utilisateur.id")
    date_commande: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    date_retrait: date
    statut: Statut = Statut.en_attente

    utilisateur: Utilisateur = Relationship(back_populates="commandes")
    lignes: list["LigneCommande"] = Relationship(back_populates="commande", cascade_delete=True)


class LigneCommande(SQLModel, table=True):
    __tablename__ = "ligne_commande"

    id: Optional[int] = Field(default=None, primary_key=True)
    commande_id: int = Field(foreign_key="commande.id", ondelete="CASCADE")
    produit_id: Optional[int] = Field(default=None, foreign_key="produit.id")  # vide si menu
    menu_id: Optional[int] = Field(default=None, foreign_key="menu.id")        # vide si produit
    quantite: int = Field(default=1, ge=1)

    commande: Commande = Relationship(back_populates="lignes")