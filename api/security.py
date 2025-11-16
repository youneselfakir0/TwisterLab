import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# --- Configuration de la Sécurité ---

from utils.secret_manager import read_secret_file

# NOTE: In production, these values MUST be loaded from Docker Secrets.
# Using hardcoded values or direct os.getenv() is ONLY for development fallback.
SECRET_KEY = read_secret_file("JWT_SECRET_KEY", "a_very_secret_key_for_dev") # Use JWT_SECRET_KEY for both
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Contexte pour le hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Schéma OAuth2 pour que FastAPI sache comment trouver le token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# --- Fonctions Utilitaires ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe en clair contre sa version hachée."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Génère le hachage d'un mot de passe."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crée un nouveau token d'accès JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- Dépendance de Sécurité FastAPI ---

async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """
    Dépendance FastAPI pour valider le token et extraire l'utilisateur.
    Cette fonction sera utilisée pour protéger les endpoints.
    Si le token est invalide, elle lève une HTTPException 401.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Dans une vraie application, on vérifierait ici que l'utilisateur existe en base de données.
    # Pour l'instant, nous retournons simplement le nom d'utilisateur.
    return username