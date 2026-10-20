# Acceso, registro y recuperación de contraseña

## Descripción
Módulo autenticacion de QuickShop, conforme al cambio quickshop-inicial.

## Modelo de datos
User: id, email único, name, password_hash, role, token_version, created_at y updated_at. PasswordReset: id, user_id, token_hash único, expires_at, used_at y created_at. Contraseña de 10 a 72 bytes UTF-8 con mayúscula, minúscula, número y símbolo. JWT de dos horas; recuperación de 20 minutos por defecto.

## API y errores
- POST /api/auth/register: {name,email,password}; 201 con usuario cliente. 409 para email duplicado; 422 para datos inválidos.
- POST /api/auth/login: {email,password}; 200 {access_token,token_type,user}; 401 para credenciales inválidas.
- POST /api/auth/forgot-password: {email}; 200 con mensaje genérico idéntico, exista o no la cuenta. Correo con enlace al frontend; nunca devolver el token en la API.
- POST /api/auth/reset-password: {token,password}; 200; 400 para token expirado, inválido o utilizado. Invalidar todos los tokens de recuperación y JWT activos.
- POST /api/auth/change-password: {current_password,password}, autenticado; 200; 400 si la contraseña actual es incorrecta. Revocar las sesiones activas.
- 401 para credenciales ausentes, expiradas o revocadas; 403 para un rol no autorizado.

## Criterios de aceptación y pantallas
- No se permite elegir rol al registrarse.
- Almacenar contraseñas exclusivamente con bcrypt; JWT solo en memoria del frontend.
- Tokens aleatorios con hash SHA-256, caducidad y uso único incluso ante solicitudes concurrentes.
- Respuesta genérica de recuperación, envío SMTP configurable y capturador local de correo para desarrollo.
- Pantallas de acceso, registro, solicitud de recuperación, nueva contraseña y cambio de contraseña.
