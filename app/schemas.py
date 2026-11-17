"""Données échangées entre le front et l'API, quand elles diffèrent de celles des tables.

Produit et Fermeture n'ont rien de sensible : les routes utilisent directement
ProduitBase / FermetureBase (entrée) et Produit / Fermeture (réponse) de models.py.
Ce fichier ne contient que les cas où une classe séparée est nécessaire.
"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models import Produit, Role, Statut


# ---------- Utilisateurs : ne jamais exposer le mot de passe ni laisser choisir le rôle ----------

class Inscription(BaseModel):
    """Le front envoie seulement le nom : le mot de passe est généré et le rôle forcé à standard."""
    nom_utilisateur: str = Field(min_length=3, max_length=50)


class InscriptionReponse(BaseModel):
    nom_utilisateur: str
    mot_de_passe: str  # mot de passe généré, transmis une seule fois


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChangementMotDePasse(BaseModel):
    ancien_mot_de_passe: str
    nouveau_mot_de_passe: str = Field(min_length=8)


class UtilisateurReponse(BaseModel):
    """Utilisateur renvoyé par l'API : SANS le champ mot_de_passe."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom_utilisateur: str
    role: Role
    bloque: bool


class Blocage(BaseModel):
    bloque: bool


#  modification partielle du stock des produits

class StockModification(BaseModel):
    stock: int = Field(ge=0)
    disponible: Optional[bool] = None


#Menus : recevoir la liste des produits / renvoyer les produits

def _verifier_dates(date_debut, date_fin):
    if date_debut and date_fin and date_fin < date_debut:
        raise ValueError("date_fin doit être postérieure ou égale à date_debut")


class MenuCreation(BaseModel):
    nom: str = Field(min_length=1)
    description: Optional[str] = None
    prix: float = Field(ge=0)
    date_debut: Optional[date] = None  # vide = menu permanent
    date_fin: Optional[date] = None
    produit_ids: list[int] = []        # pas une colonne : sert à remplir menu_produit

    @model_validator(mode="after")
    def verifier_dates(self):
        _verifier_dates(self.date_debut, self.date_fin)
        return self


class MenuDisponibilite(BaseModel):
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None

    @model_validator(mode="after")
    def verifier_dates(self):
        _verifier_dates(self.date_debut, self.date_fin)
        return self


class MenuReponse(BaseModel):
    """Menu renvoyé avec la liste de ses produits."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    description: Optional[str]
    prix: float
    date_debut: Optional[date]
    date_fin: Optional[date]
    produits: list[Produit]


#  Commandes : règle produit ou menu, et total calculé

class LigneCommandeCreation(BaseModel):
    produit_id: Optional[int] = None
    menu_id: Optional[int] = None
    quantite: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def produit_ou_menu(self):
        # Même règle que le CHECK de schema.sql
        if (self.produit_id is None) == (self.menu_id is None):
            raise ValueError("Indiquer soit produit_id, soit menu_id")
        return self


class CommandeCreation(BaseModel):
    date_retrait: date
    lignes: list[LigneCommandeCreation] = Field(min_length=1)


class LigneCommandeReponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    produit_id: Optional[int]
    menu_id: Optional[int]
    quantite: int


class CommandeReponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    utilisateur_id: int
    date_commande: datetime
    date_retrait: date
    statut: Statut
    lignes: list[LigneCommandeReponse]
    total: float  # calculé par le back, non stocké en base


class StatutModification(BaseModel):
    statut: Statut