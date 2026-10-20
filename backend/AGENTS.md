# Backend
- Respetar AGENTS.md de la raíz. Usar bcrypt directamente, sin passlib.
- Validar entradas con Pydantic y email-validator. Nunca serializar hashes ni tokens de recuperación.
- Mantener transacciones en la dependencia de sesión. Usar bloqueos de filas en pedidos, stock y recuperación.
- Alembic gestiona el esquema; no usar create_all al arrancar la aplicación.
- Envío de correo desacoplado: SMTP en ejecución y proveedor en memoria para tests.
- Los tests usan una base aislada; nunca apuntarlos a la base de desarrollo.
