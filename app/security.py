import secrets
import string
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.config import ALGORITHM, SECRET_KEY, TOKEN_EXPIRE_MINUTES

# Hacheur de mots de passe (algorithme argon2)
password_hash = PasswordHash.recommended()


#Mots de passe

def hacher_mot_de_passe(mot_de_passe: str) -> str:
    """Transforme 'abc123' en '$argon2id$v=19$...' (irréversible)."""
    return password_hash.hash(mot_de_passe)


def verifier_mot_de_passe(mot_de_passe: str, hash_stocke: str) -> bool:
    """Compare un mot de passe saisi avec le hash stocké en base."""
    return password_hash.verify(mot_de_passe, hash_stocke)


def generer_mot_de_passe(longueur: int = 12) -> str:
    """Mot de passe aléatoire pour l'inscription (secrets = aléatoire sûr)."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(longueur))


# Tokens JWT

def creer_token(utilisateur_id: int) -> str:
    """Crée un token signé contenant l'id de l'utilisateur et une date d'expiration."""
    expiration = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    contenu = {"sub": str(utilisateur_id), "exp": expiration}
    return jwt.encode(contenu, SECRET_KEY, algorithm=ALGORITHM)


def decoder_token(token: str) -> int | None:
    """Renvoie l'id de l'utilisateur si le token est valide, sinon None."""
    try:
        contenu = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(contenu["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        # si le token falsifié, expiré, ou mal formé on retourne ca
        return None