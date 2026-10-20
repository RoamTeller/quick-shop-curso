# Perfil y separación de roles

## Descripción
Módulo usuarios de QuickShop, conforme al cambio quickshop-inicial.

## Modelo de datos
User: email único normalizado, nombre, rol cliente/administrador y timestamps. No exponer password_hash ni token_version.

## API y errores
- GET /api/users/me: Bearer JWT; 200 con perfil propio; 401 si no hay sesión válida.
- 401 para credenciales ausentes, expiradas o revocadas; 403 para un rol no autorizado.

## Criterios de aceptación y pantallas
- Seed idempotente de un administrador y dos clientes, con credenciales desde entorno.
- Un cliente ve únicamente su perfil y sus recursos.
- Backend rechaza acceso administrativo de clientes con 403.
- Pantalla de perfil con cambio de contraseña; navegación según rol.
