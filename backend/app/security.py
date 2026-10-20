from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .config import get_settings
from .database import get_db
from .models import User

bearer = HTTPBearer(auto_error=False)
DUMMY_HASH = bcrypt.hashpw(b"Dummy-password-123!", bcrypt.gensalt(rounds=12))

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=get_settings().bcrypt_rounds)).decode()

def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode())
    except (ValueError, TypeError):
        return False

def create_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": str(user.id), "ver": user.token_version, "iat": now, "exp": now + timedelta(hours=2), "iss": "quickshop", "aud": "quickshop-web"}, get_settings().jwt_secret.get_secret_value(), algorithm="HS256")

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    error = HTTPException(401, "La sesión no es válida o ha caducado.", headers={"WWW-Authenticate": "Bearer"})
    if not credentials:
        raise error
    try:
        claims = jwt.decode(credentials.credentials, get_settings().jwt_secret.get_secret_value(), algorithms=["HS256"], issuer="quickshop", audience="quickshop-web", options={"require": ["sub", "ver", "iat", "exp"]})
        user = db.get(User, int(claims["sub"]))
        if not user or type(claims["ver"]) is not int or user.token_version != claims["ver"]:
            raise error
        return user
    except (jwt.InvalidTokenError, ValueError, TypeError, KeyError):
        raise error

def admin_user(user: User = Depends(current_user)) -> User:
    if user.role != "administrador":
        raise HTTPException(403, "Esta acción requiere permisos de administrador.")
    return user

def client_user(user: User = Depends(current_user)) -> User:
    if user.role != "cliente":
        raise HTTPException(403, "El administrador no dispone de carrito ni realiza compras.")
    return user
