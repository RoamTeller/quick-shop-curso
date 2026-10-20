# Diseño técnico

## Arquitectura

Se separan `backend/` y `frontend/`, orquestados por `docker-compose`. FastAPI expone una API REST y PostgreSQL almacena usuarios, productos, carritos, líneas de carrito, pedidos y líneas de pedido. React consume la API mediante un cliente centralizado.

## Seguridad

Las contraseñas se protegen con bcrypt. Los access tokens JWT duran dos horas y no se guardan en localStorage. Los secretos y URLs se leen desde variables de entorno; `.env.example` documenta las variables necesarias.

La recuperación de contraseña usa tokens aleatorios de un solo uso, con expiración corta y almacenamiento mediante hash. El endpoint de solicitud devuelve siempre una respuesta indistinguible para emails existentes y no existentes. El envío se abstrae detrás de un proveedor configurable para desarrollo y producción. Al completar el cambio se invalidan los tokens de recuperación previos y las sesiones activas del usuario.

## Persistencia y consistencia

Alembic se ejecuta al arrancar el backend. El seed es idempotente. La creación y cancelación de pedidos actualiza stock dentro de transacciones, con validación de disponibilidad y restricciones de estado.

## Frontend

React Router organiza las páginas públicas, autenticadas y administrativas. Un layout común contiene el header y navegación responsive. Las rutas y acciones sensibles se protegen también en backend, no solo en la interfaz.

## Decisiones operativas

Se usa bcrypt directamente, `email-validator`, Node 22 Alpine y pnpm 11. `pnpm-workspace.yaml` se copia antes de instalar dependencias y declara `allowBuilds`. El Dockerfile excluye `node_modules` mediante `.dockerignore`.
