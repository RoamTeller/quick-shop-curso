from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from .config import get_settings
from .database import engine
from .auth import router as auth_router
from .commerce import router as commerce_router

settings = get_settings()
app = FastAPI(title="QuickShop API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=[str(settings.frontend_base_url).rstrip("/")], allow_credentials=False, allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"], allow_headers=["Authorization", "Content-Type"])
app.include_router(auth_router)
app.include_router(commerce_router)

@app.get("/api/health")
def health():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ok"}
