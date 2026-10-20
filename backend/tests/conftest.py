import os
import subprocess
from uuid import uuid4
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

original_url = make_url(os.environ["DATABASE_URL"])
test_name = "quickshop_test_" + uuid4().hex[:12]
admin_engine = create_engine(original_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
with admin_engine.connect() as connection:
    connection.execute(text(f'CREATE DATABASE "{test_name}"'))
os.environ["DATABASE_URL"] = original_url.set(database=test_name).render_as_string(hide_password=False)
os.environ.update(EMAIL_PROVIDER="memory", BCRYPT_ROUNDS="4", FRONTEND_BASE_URL="http://testserver", SEED_ADMIN_EMAIL="admin@example.com", SEED_ADMIN_PASSWORD="Admin-test123!", SEED_CLIENT1_EMAIL="one@example.com", SEED_CLIENT1_PASSWORD="Client-test123!", SEED_CLIENT2_EMAIL="two@example.com", SEED_CLIENT2_PASSWORD="Client-test123!")
subprocess.run(["uv", "run", "alembic", "upgrade", "head"], check=True)
from app.database import engine, SessionLocal
from app.main import app
from app.seed import seed
from app.email_service import outbox
from fastapi.testclient import TestClient

@pytest.fixture(scope="session", autouse=True)
def database_lifecycle():
    yield
    engine.dispose()
    assert test_name.startswith("quickshop_test_")
    with admin_engine.connect() as connection:
        connection.execute(text(f'DROP DATABASE "{test_name}" WITH (FORCE)'))
    admin_engine.dispose()

@pytest.fixture(autouse=True)
def clean_database():
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE order_items, orders, cart_items, carts, password_resets, products, users RESTART IDENTITY CASCADE"))
    outbox.clear()
    seed()

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

def login_headers(client, email="one@example.com", password="Client-test123!"):
    response = client.post("/api/auth/login", json={"email":email,"password":password})
    assert response.status_code == 200
    return {"Authorization": "Bearer " + response.json()["access_token"]}

@pytest.fixture
def customer(client):
    return login_headers(client)

@pytest.fixture
def admin(client):
    return login_headers(client, "admin@example.com", "Admin-test123!")
