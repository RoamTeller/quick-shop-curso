"""Comprobación HTTP del entorno Docker; crea un cliente de prueba y un pedido cancelado."""
import os
import re
import sys
import time
from uuid import uuid4
import httpx

api_url, mail_url, frontend_url = sys.argv[1:4]
email = "smoke-" + uuid4().hex[:12] + "@example.com"
password = "Smoke-" + uuid4().hex + "1!"
new_password = "Updated-" + uuid4().hex + "2!"
with httpx.Client(base_url=api_url, timeout=15) as client:
    assert client.get("/api/health").status_code == 200
    products = client.get("/api/products").json()
    assert len(products) == 20
    proxy_response = httpx.get(frontend_url + "/api/products", headers={"Host": "localhost"})
    assert proxy_response.status_code == 200
    assert len(proxy_response.json()) == 20
    product = next(p for p in products if p["stock"] > 0)
    assert client.post("/api/auth/register", json={"email": email, "name": "Prueba automática", "password": password}).status_code == 201
    auth = client.post("/api/auth/login", json={"email": email, "password": password}).json()
    headers = {"Authorization": "Bearer " + auth["access_token"]}
    assert client.get("/api/admin/products", headers=headers).status_code == 403
    assert client.post("/api/cart/items", headers=headers, json={"product_id": product["id"], "quantity": 1}).status_code == 200
    result = client.post("/api/orders", headers=headers)
    assert result.status_code == 201
    order = result.json()
    assert client.get("/api/products/" + str(product["id"])).json()["stock"] == product["stock"] - 1
    admin = client.post("/api/auth/login", json={"email": os.environ["SEED_ADMIN_EMAIL"], "password": os.environ["SEED_ADMIN_PASSWORD"]}).json()
    admin_headers = {"Authorization": "Bearer " + admin["access_token"]}
    path = "/api/admin/orders/" + str(order["id"]) + "/status"
    assert client.patch(path, headers=admin_headers, json={"status": "confirmado"}).status_code == 200
    assert client.post("/api/orders/" + str(order["id"]) + "/cancel", headers=headers).status_code == 409
    assert client.patch(path, headers=admin_headers, json={"status": "cancelado"}).status_code == 200
    assert client.get("/api/products/" + str(product["id"])).json()["stock"] == product["stock"]
    print("HTTP: catálogo, proxy, registro, acceso, roles, carrito, pedido, confirmación y cancelación correctos.")
    known = client.post("/api/auth/forgot-password", json={"email": email})
    unknown = client.post("/api/auth/forgot-password", json={"email": "absent-" + email})
    assert known.status_code == unknown.status_code == 200 and known.json() == unknown.json()
    token = None
    for _ in range(15):
        messages = httpx.get(mail_url + "/api/v1/messages").json().get("messages", [])
        target = next((m for m in messages if any(t.get("Address") == email for t in m.get("To", []))), None)
        if target:
            message = httpx.get(mail_url + "/api/v1/message/" + target["ID"]).json()
            match = re.search(r"#token=([A-Za-z0-9_-]+)", message.get("Text", ""))
            if match:
                token = match.group(1)
                break
        time.sleep(0.2)
    assert token, "No se recibió el correo en Mailpit."
    assert client.post("/api/auth/reset-password", json={"token": token, "password": new_password}).status_code == 200
    assert client.get("/api/users/me", headers=headers).status_code == 401
    assert client.post("/api/auth/reset-password", json={"token": token, "password": new_password}).status_code == 400
    assert client.post("/api/auth/login", json={"email": email, "password": new_password}).status_code == 200
    print("SMTP: correo capturado, recuperación, invalidación de sesión y token de un solo uso correctos.")
