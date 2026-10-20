# QuickShop

Mini tienda del curso Desarrollo con IA. React 18, Vite, Tailwind CSS y React Router en frontend; Python 3.11, FastAPI, SQLAlchemy 2, Alembic y PostgreSQL 15 en backend.

## Arranque en Windows

Requisitos: Docker Desktop con el motor Linux en marcha y Node.js para preparar el entorno.

En la terminal de VS Code, desde esta carpeta:

```powershell
node scripts/init-env.mjs
docker compose up --build -d
docker compose ps
```

El primer comando crea .env con secretos aleatorios solo si no existe. Conserva la configuración existente. No versionar ni compartir .env.

- Tienda: http://localhost:5173
- API y documentación interactiva: http://localhost:8000/docs
- Correos de recuperación de desarrollo: http://localhost:8025

Los puertos se publican únicamente en la interfaz local. FRONTEND_PORT, BACKEND_PORT y MAILPIT_PORT permiten cambiarlos en .env. Si cambias FRONTEND_PORT, actualiza también FRONTEND_BASE_URL y recrea los servicios con docker compose up -d.

Para detener sin perder los datos: `docker compose down`. Los datos viven en el volumen quickshop_data; no usar down -v si deseas conservarlos.

## Cuentas de demostración

El seed crea un administrador y dos clientes usando las variables SEED_* del entorno. En .env.example se documentan las cuentas del curso. Las contraseñas se transforman en hashes bcrypt; no están incrustadas en el código de aplicación.

- Administrador: admin@quickshop.com / Admin1234!
- Clientes: cliente1@quickshop.com y cliente2@quickshop.com / Cliente1234!

Estas cuentas son para el ejercicio local. Cambiar las variables después de haber ejecutado el seed no cambia las contraseñas existentes: el seed conserva los usuarios.

## Funcionalidad

Registro y acceso, perfil, cambio y recuperación de contraseña, catálogo de 20 productos, carrito privado, pedidos y administración. El navegador mantiene el JWT únicamente en memoria; recargar la página requiere iniciar sesión de nuevo. La expiración es de dos horas. Cambiar la contraseña revoca todas las sesiones del usuario.

La recuperación devuelve el mismo mensaje para direcciones registradas y no registradas. El correo incluye un token aleatorio de uso único con 20 minutos de validez por defecto, almacenado en la base de datos mediante hash. Mailpit captura el correo dentro del entorno local; no se envía a direcciones reales. Para otro servidor SMTP configurar EMAIL_PROVIDER, SMTP_HOST, SMTP_PORT, SMTP_STARTTLS, SMTP_USERNAME, SMTP_PASSWORD y EMAIL_FROM. EMAIL_PROVIDER=memory se reserva para tests.

El stock se descuenta al crear el pedido pendiente, dentro de una transacción con bloqueo de filas. Confirmar o enviar no vuelve a restarlo. Las cancelaciones válidas lo reponen una sola vez. El cliente puede cancelar solamente sus pedidos pendientes. El administrador puede avanzar estados y cancelar pendientes, confirmados o enviados. Entregado y cancelado son estados finales.

No incluye pagos reales ni integraciones de envío.

## Pruebas

```powershell
docker compose run --rm --no-deps backend uv run pytest -q
docker compose run --rm --no-deps frontend pnpm test
docker compose run --rm --no-deps frontend pnpm build
```

El servicio db debe estar arrancado. Los tests backend crean una base con nombre quickshop_test_* aislada y la eliminan al terminar; nunca vacían la base de desarrollo. Cubren roles, recuperación, expiración, invalidación de sesiones, stock, cancelaciones y solicitudes concurrentes. Los tests frontend verifican catálogo, búsqueda, agotados, acceso y navegación protegida.

Para ver registros: `docker compose logs --tail=50 backend frontend`.

## Estructura y OpenSpec

- backend/app: configuración, API, modelos y servicios.
- backend/migrations: esquema versionado mediante Alembic.
- backend/tests: pruebas sobre PostgreSQL real.
- frontend/src: interfaz y pruebas.
- docs/specs-prds: requisitos de los cinco módulos.
- openspec/changes/quickshop-inicial: propuesta, diseño, especificaciones y tareas.

Las migraciones y el seed se ejecutan automáticamente al arrancar el backend. El archivo pnpm-workspace.yaml contiene allowBuilds y se copia antes de instalar dependencias en Docker. Cada capa dispone de AGENTS.md; CLAUDE.md referencia esas reglas para evitar duplicarlas.
