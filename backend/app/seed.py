import json
from decimal import Decimal
from sqlalchemy import select, func
from .config import get_settings
from .database import SessionLocal
from .models import User, Product, Cart
from .schemas import validate_password
from .security import hash_password

def seed():
    settings = get_settings()
    accounts = [
        (settings.seed_admin_email, settings.seed_admin_password, "Administración", "administrador"),
        (settings.seed_client1_email, settings.seed_client1_password, "Cliente Uno", "cliente"),
        (settings.seed_client2_email, settings.seed_client2_password, "Cliente Dos", "cliente"),
    ]
    with SessionLocal.begin() as db:
        for email, password, name, role in accounts:
            user = db.scalar(select(User).where(User.email == email.lower()))
            if not user:
                raw = validate_password(password.get_secret_value())
                user = User(email=email.lower(), name=name, role=role, password_hash=hash_password(raw))
                db.add(user)
                db.flush()
            if role == "cliente" and not db.scalar(select(Cart.id).where(Cart.user_id == user.id)):
                db.add(Cart(user_id=user.id))
        if db.scalar(select(func.count()).select_from(Product)) == 0:
            products = json.loads(settings.products_file.read_text(encoding="utf-8"))
            if len(products) != 20:
                raise ValueError("El catálogo inicial debe contener exactamente 20 productos.")
            for item in products:
                db.add(Product(name=item["producto"], description=item["descripcion"], price=Decimal(item["precio"]), stock=item["stock"], image_url=item["imagen"], is_active=True))

if __name__ == "__main__":
    seed()
