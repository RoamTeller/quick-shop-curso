from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import jwt
import pytest
from sqlalchemy import select, func
from fastapi.testclient import TestClient
from app.database import SessionLocal
from app.models import User, PasswordReset, Product
from app.email_service import outbox
from app.main import app
from app.seed import seed
from .conftest import login_headers

def reset_token():
    return outbox[-1]["url"].split("#token=")[1]

def buy(client, headers, quantity=2, product_id=1):
    assert client.post("/api/cart/items", headers=headers, json={"product_id":product_id,"quantity":quantity}).status_code == 200
    result = client.post("/api/orders", headers=headers)
    assert result.status_code == 201
    return result.json()

def test_seed_is_idempotent():
    seed()
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(User)) == 3
        assert db.scalar(select(func.count()).select_from(Product)) == 20

def test_login_profile_and_expiry(client, customer):
    response = client.get("/api/users/me", headers=customer)
    assert response.status_code == 200 and response.json()["role"] == "cliente"
    assert "password_hash" not in response.json()
    token = customer["Authorization"].split()[1]
    claims = jwt.decode(token, options={"verify_signature":False})
    assert claims["exp"] - claims["iat"] == 7200
    assert client.get("/api/users/me", headers={"Authorization":"Bearer invalid"}).status_code == 401

def test_bad_login_and_unknown_email_match(client):
    a = client.post("/api/auth/login", json={"email":"one@example.com","password":"wrong"})
    b = client.post("/api/auth/login", json={"email":"absent@example.com","password":"wrong"})
    assert a.status_code == b.status_code == 401 and a.json() == b.json()

def test_register_role_password_and_uniqueness(client):
    data={"name":"Nuevo Cliente","email":"NEW@example.com","password":"Strong-new123!"}
    assert client.post("/api/auth/register",json={**data,"role":"administrador"}).status_code == 422
    response=client.post("/api/auth/register",json=data)
    assert response.status_code == 201 and response.json()["email"] == "new@example.com"
    assert response.json()["role"] == "cliente"
    assert client.post("/api/auth/register",json=data).status_code == 409
    assert client.post("/api/auth/register",json={**data,"email":"other@example.com","password":"weak"}).status_code == 422

def test_roles(client, customer, admin):
    assert client.get("/api/admin/products",headers=customer).status_code == 403
    assert client.get("/api/cart",headers=admin).status_code == 403
    assert client.post("/api/orders",headers=admin).status_code == 403
    assert client.get("/api/orders").status_code == 401

def test_recovery_does_not_enumerate_or_return_token(client):
    a=client.post("/api/auth/forgot-password",json={"email":"one@example.com"})
    b=client.post("/api/auth/forgot-password",json={"email":"absent@example.com"})
    assert a.status_code == b.status_code == 200 and a.json() == b.json()
    assert len(outbox) == 1
    token=reset_token()
    with SessionLocal() as db:
        record=db.scalar(select(PasswordReset))
        assert record.token_hash == hashlib.sha256(token.encode()).hexdigest()
        assert record.token_hash != token

def test_reset_revokes_sessions_and_single_use(client, customer):
    client.post("/api/auth/forgot-password",json={"email":"one@example.com"})
    token=reset_token()
    assert client.post("/api/auth/reset-password",json={"token":token,"password":"Another-good123!"}).status_code == 200
    assert client.get("/api/users/me",headers=customer).status_code == 401
    assert client.post("/api/auth/reset-password",json={"token":token,"password":"Third-good123!"}).status_code == 400
    assert client.post("/api/auth/login",json={"email":"one@example.com","password":"Client-test123!"}).status_code == 401
    assert client.post("/api/auth/login",json={"email":"one@example.com","password":"Another-good123!"}).status_code == 200

def test_reset_expiry_invalid_and_password_policy(client):
    client.post("/api/auth/forgot-password",json={"email":"one@example.com"})
    token=reset_token()
    assert client.post("/api/auth/reset-password",json={"token":token,"password":"weak"}).status_code == 422
    with SessionLocal.begin() as db:
        db.scalar(select(PasswordReset)).expires_at=datetime.now(timezone.utc)-timedelta(minutes=1)
    assert client.post("/api/auth/reset-password",json={"token":token,"password":"Another-good123!"}).status_code == 400
    assert client.post("/api/auth/reset-password",json={"token":"x"*43,"password":"Another-good123!"}).status_code == 400

def test_new_recovery_invalidates_previous_token(client):
    client.post("/api/auth/forgot-password",json={"email":"one@example.com"}); old=reset_token()
    client.post("/api/auth/forgot-password",json={"email":"one@example.com"}); new=reset_token()
    assert client.post("/api/auth/reset-password",json={"token":old,"password":"Another-good123!"}).status_code == 400
    assert client.post("/api/auth/reset-password",json={"token":new,"password":"Another-good123!"}).status_code == 200

def test_change_password_requires_current_and_revokes_all(client, customer):
    other=login_headers(client)
    client.post("/api/auth/forgot-password",json={"email":"one@example.com"}); token=reset_token()
    assert client.post("/api/auth/change-password",headers=customer,json={"current_password":"incorrect","password":"Another-good123!"}).status_code == 400
    assert client.post("/api/auth/change-password",headers=customer,json={"current_password":"Client-test123!","password":"Another-good123!"}).status_code == 200
    assert client.get("/api/users/me",headers=other).status_code == 401
    assert client.post("/api/auth/reset-password",json={"token":token,"password":"Third-good123!"}).status_code == 400

def test_simultaneous_reset_only_one_succeeds(client):
    client.post("/api/auth/forgot-password",json={"email":"one@example.com"}); token=reset_token()
    def run():
        with TestClient(app) as concurrent:
            return concurrent.post("/api/auth/reset-password",json={"token":token,"password":"Another-good123!"}).status_code
    with ThreadPoolExecutor(max_workers=2) as executor:
        assert sorted(executor.map(lambda _:run(), range(2))) == [200,400]

def test_catalog_and_admin_product_lifecycle(client,admin):
    assert len(client.get("/api/products").json()) == 20
    product={"name":"Producto nuevo","description":"Descripción del producto","price":"12.35","stock":5,"image_url":"https://example.com/product.jpg","is_active":True}
    response=client.post("/api/admin/products",headers=admin,json=product)
    assert response.status_code == 201
    pid=response.json()["id"]
    assert response.json()["price"] == "12.35"
    assert client.put(f"/api/admin/products/{pid}",headers=admin,json={**product,"price":"12.351"}).status_code == 422
    assert client.put(f"/api/admin/products/{pid}",headers=admin,json={**product,"stock":-1}).status_code == 422
    assert client.put(f"/api/admin/products/{pid}",headers=admin,json={**product,"stock":0}).status_code == 200
    assert client.get(f"/api/products/{pid}").json()["stock"] == 0
    assert client.delete(f"/api/admin/products/{pid}",headers=admin).status_code == 204
    assert client.get(f"/api/products/{pid}").status_code == 404
    assert len(client.get("/api/admin/products",headers=admin).json()) == 21

def test_cart_quantity_stock_isolation_and_remove(client,customer):
    assert client.post("/api/cart/items",headers=customer,json={"product_id":1,"quantity":0}).status_code == 422
    assert client.post("/api/cart/items",headers=customer,json={"product_id":1,"quantity":11}).status_code == 409
    assert client.post("/api/cart/items",headers=customer,json={"product_id":1,"quantity":2}).status_code == 200
    response=client.post("/api/cart/items",headers=customer,json={"product_id":1,"quantity":3})
    assert response.json()["items"][0]["quantity"] == 5
    other=login_headers(client,"two@example.com")
    assert client.get("/api/cart",headers=other).json()["items"] == []
    assert client.delete("/api/cart/items/1",headers=other).status_code == 404
    assert client.patch("/api/cart/items/1",headers=customer,json={"quantity":6}).status_code == 200
    assert client.patch("/api/cart/items/1",headers=customer,json={"quantity":11}).status_code == 409
    assert client.delete("/api/cart/items/1",headers=customer).status_code == 204
    assert client.get("/api/cart",headers=customer).json()["items"] == []

def test_sold_out_visible_but_unavailable(client,customer):
    with SessionLocal.begin() as db: db.get(Product,1).stock=0
    assert any(p["id"]==1 and p["stock"]==0 for p in client.get("/api/products").json())
    assert client.post("/api/cart/items",headers=customer,json={"product_id":1,"quantity":1}).status_code == 409

def test_checkout_snapshots_stock_and_ownership(client,customer,admin):
    order=buy(client,customer)
    assert order["status"] == "pendiente" and Decimal(order["total"]) == Decimal("2599.98")
    assert client.get("/api/products/1").json()["stock"] == 8
    assert client.get("/api/cart",headers=customer).json()["items"] == []
    other=login_headers(client,"two@example.com")
    assert client.get(f'/api/orders/{order["id"]}',headers=other).status_code == 404
    assert client.post(f'/api/orders/{order["id"]}/cancel',headers=other).status_code == 404
    assert len(client.get("/api/orders",headers=admin).json()) == 1
    assert client.patch(f'/api/admin/orders/{order["id"]}/status',headers=customer,json={"status":"confirmado"}).status_code == 403
    with SessionLocal.begin() as db: db.get(Product,1).price=Decimal("5.00")
    assert client.get(f'/api/orders/{order["id"]}',headers=customer).json()["items"][0]["unit_price"] == "1299.99"

@pytest.mark.parametrize("target",["pendiente","confirmado","enviado"])
def test_cancellation_restores_once(client,customer,admin,target):
    order=buy(client,customer)
    for status in (["confirmado","enviado"] if target=="enviado" else ["confirmado"] if target=="confirmado" else []):
        assert client.patch(f'/api/admin/orders/{order["id"]}/status',headers=admin,json={"status":status}).status_code == 200
        assert client.get("/api/products/1").json()["stock"] == 8
    headers=customer if target=="pendiente" else admin
    if target!="pendiente": assert client.post(f'/api/orders/{order["id"]}/cancel',headers=customer).status_code == 409
    assert client.post(f'/api/orders/{order["id"]}/cancel',headers=headers).status_code == 200
    assert client.get("/api/products/1").json()["stock"] == 10
    assert client.post(f'/api/orders/{order["id"]}/cancel',headers=headers).status_code == 409
    assert client.get("/api/products/1").json()["stock"] == 10

def test_invalid_transitions_and_delivered_order(client,customer,admin):
    order=buy(client,customer); path=f'/api/admin/orders/{order["id"]}/status'
    assert client.patch(path,headers=admin,json={"status":"entregado"}).status_code == 409
    for status in ["confirmado","enviado","entregado"]:
        assert client.patch(path,headers=admin,json={"status":status}).status_code == 200
    assert client.post(f'/api/orders/{order["id"]}/cancel',headers=admin).status_code == 409
    assert client.get("/api/products/1").json()["stock"] == 8

def test_checkout_rolls_back_every_product_if_stock_changes(client,customer):
    for pid in [1,2]: assert client.post("/api/cart/items",headers=customer,json={"product_id":pid,"quantity":2}).status_code == 200
    with SessionLocal.begin() as db: db.get(Product,2).stock=0
    assert client.post("/api/orders",headers=customer).status_code == 409
    assert client.get("/api/products/1").json()["stock"] == 10
    assert len(client.get("/api/cart",headers=customer).json()["items"]) == 2
    assert client.get("/api/orders",headers=customer).json() == []

def test_competing_checkouts_cannot_oversell(client,customer):
    other=login_headers(client,"two@example.com")
    with SessionLocal.begin() as db: db.get(Product,1).stock=1
    for headers in [customer,other]: assert client.post("/api/cart/items",headers=headers,json={"product_id":1,"quantity":1}).status_code == 200
    def run(headers):
        with TestClient(app) as concurrent:
            return concurrent.post("/api/orders",headers=headers).status_code
    with ThreadPoolExecutor(max_workers=2) as executor:
        assert sorted(executor.map(run,[customer,other])) == [201,409]
    assert client.get("/api/products/1").json()["stock"] == 0

def test_duplicate_checkout_same_cart_only_one_order(client,customer):
    client.post("/api/cart/items",headers=customer,json={"product_id":1,"quantity":1})
    def run():
        with TestClient(app) as concurrent:
            return concurrent.post("/api/orders",headers=customer).status_code
    with ThreadPoolExecutor(max_workers=2) as executor:
        assert sorted(executor.map(lambda _:run(),range(2))) == [201,409]
    assert client.get("/api/products/1").json()["stock"] == 9
    assert len(client.get("/api/orders",headers=customer).json()) == 1

def test_cors(client):
    allowed=client.options("/api/products",headers={"Origin":"http://testserver","Access-Control-Request-Method":"GET"})
    denied=client.options("/api/products",headers={"Origin":"https://other.example","Access-Control-Request-Method":"GET"})
    assert allowed.headers.get("access-control-allow-origin") == "http://testserver"
    assert "access-control-allow-origin" not in denied.headers
