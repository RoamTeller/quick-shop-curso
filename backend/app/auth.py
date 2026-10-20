from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .config import get_settings
from .database import get_db
from .models import User, Cart, PasswordReset
from .schemas import RegisterInput, LoginInput, ResetInput, ChangePasswordInput, EmailInput, LoginOut, UserOut, Message
from .security import current_user, hash_password, verify_password, create_token, DUMMY_HASH
from .email_service import send_reset_email

router = APIRouter(prefix="/api", tags=["Autenticación"])
GENERIC_MESSAGE = "Si la dirección está registrada, recibirás un correo con los siguientes pasos."

def invalidate_sessions(db: Session, user: User):
    user.token_version += 1
    db.execute(update(PasswordReset).where(PasswordReset.user_id == user.id, PasswordReset.used_at.is_(None)).values(used_at=datetime.now(timezone.utc)))

@router.post("/auth/register", response_model=UserOut, status_code=201)
def register(data: RegisterInput, db: Session = Depends(get_db)):
    if db.scalar(select(User.id).where(User.email == data.email)):
        raise HTTPException(409, "No se puede registrar esa dirección.")
    user = User(email=data.email, name=data.name, password_hash=hash_password(data.password.get_secret_value()), role="cliente")
    db.add(user)
    try:
        db.flush()
    except IntegrityError:
        raise HTTPException(409, "No se puede registrar esa dirección.")
    db.add(Cart(user_id=user.id))
    db.flush()
    return user

@router.post("/auth/login", response_model=LoginOut)
def login(data: LoginInput, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email))
    hashed = user.password_hash if user else DUMMY_HASH.decode()
    valid = verify_password(data.password.get_secret_value(), hashed)
    if not user or not valid:
        raise HTTPException(401, "Email o contraseña incorrectos.", headers={"WWW-Authenticate": "Bearer"})
    return {"access_token": create_token(user), "user": user}

@router.get("/users/me", response_model=UserOut)
def profile(user: User = Depends(current_user)):
    return user

@router.post("/auth/forgot-password", response_model=Message)
def forgot(data: EmailInput, background: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email).with_for_update())
    token = secrets.token_urlsafe(32)
    digest = hashlib.sha256(token.encode()).hexdigest()
    if user:
        now = datetime.now(timezone.utc)
        db.execute(update(PasswordReset).where(PasswordReset.user_id == user.id, PasswordReset.used_at.is_(None)).values(used_at=now))
        db.add(PasswordReset(user_id=user.id, token_hash=digest, expires_at=now + timedelta(minutes=get_settings().reset_minutes)))
        db.flush()
        url = str(get_settings().frontend_base_url).rstrip("/") + "/restablecer#token=" + token
        background.add_task(send_reset_email, user.email, url)
    return {"message": GENERIC_MESSAGE}

@router.post("/auth/reset-password", response_model=Message)
def reset(data: ResetInput, db: Session = Depends(get_db)):
    digest = hashlib.sha256(data.token.encode()).hexdigest()
    user_id = db.scalar(select(PasswordReset.user_id).where(PasswordReset.token_hash == digest))
    if user_id is None:
        raise HTTPException(400, "El enlace no es válido o ha caducado.")
    user = db.scalar(select(User).where(User.id == user_id).with_for_update())
    reset_token = db.scalar(select(PasswordReset).where(PasswordReset.token_hash == digest).with_for_update())
    if not reset_token or reset_token.used_at or reset_token.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(400, "El enlace no es válido o ha caducado.")
    user.password_hash = hash_password(data.password.get_secret_value())
    invalidate_sessions(db, user)
    db.flush()
    return {"message": "Contraseña actualizada. Inicia sesión de nuevo."}

@router.post("/auth/change-password", response_model=Message)
def change_password(data: ChangePasswordInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.id == user.id).with_for_update().execution_options(populate_existing=True))
    if not verify_password(data.current_password.get_secret_value(), user.password_hash):
        raise HTTPException(400, "La contraseña actual no es correcta.")
    user.password_hash = hash_password(data.password.get_secret_value())
    invalidate_sessions(db, user)
    db.flush()
    return {"message": "Contraseña actualizada. Inicia sesión de nuevo."}
