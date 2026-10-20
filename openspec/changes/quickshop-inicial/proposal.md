# Propuesta: QuickShop inicial

## Qué se quiere construir

Crear una mini plataforma de comercio electrónico con React/Vite/Tailwind en el frontend y FastAPI, SQLAlchemy, Alembic y PostgreSQL en el backend. La primera entrega cubrirá autenticación, usuarios, catálogo, carrito y pedidos, con ejecución reproducible mediante Docker Compose.

## Por qué

El proyecto necesita una base funcional y estable que permita a clientes comprar productos y a administradores gestionar el catálogo y los pedidos.

## Alcance

- Autenticación JWT y roles cliente/administrador.
- Recuperación segura de contraseñas mediante email.
- Catálogo de 20 productos sembrados desde `docs/products-images.json`.
- Carrito con validación de stock.
- Creación, consulta y cancelación condicionada de pedidos.
- Gestión administrativa de productos y estados de pedidos.
- Migraciones, seed idempotente, CORS, variables de entorno y Docker Compose.
- Documentación modular y convenciones para agentes.

## Fuera de alcance

Pagos reales, registro social, envíos externos, cupones, reseñas y notificaciones.

## Criterio de éxito

Una instalación limpia mediante Docker puede arrancar ambos servicios, ejecutar migraciones y seed, autenticar usuarios y completar el flujo catálogo → carrito → pedido respetando roles y stock.
