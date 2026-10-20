## Contexto del proyecto

Proyecto: QuickShop, mini plataforma de e-commerce.
Objetivo: aplicacion moderna, funcional y estable.

## Stack

- Frontend: React 18 + Vite + Tailwind CSS + React Router
- Backend: Python 3.11 + FastAPI + SQLAlchaemy 2.0 + Alembic
- Base de datos: PostgreSQL 15
- Despliegue: Docker + docker-compose
- Gestor de dependencias: pnpm para frontend + uv para backend

## Dominio

Usuarios:

- Rol cliente: registro, login, ver catalogo, gestionar carrito, crear pedidos, ver historial, cancelar pedido propio si esta pendiente
- Rol administrador: login, CRUD de productos, gestion del estado de pedidos de cualquier cliente
- El administrador se crea por seed,

Catalogo:

- 20 productos creados por seed en base al fichero ubicado en docs/products-images.json
- Campos: nombre, descripcion, precio (Decimal con 2 decimales, > 0), stock (entero >= 0), URL de imagen, flag is_active
- Producto con stock 0: visible pero deshabilitado para agregar al carrito

Carrito:

- Operaciones: agregar item, modificar cantidad, eliminar item, vaciar
- No se puede agregar mas cantidad que el stock disponible
- El admin no tiene carrito

Pedidos:

- Solo el admin cambia el estado, con una excepcion: el cliente puede cancelar su propio pedido si y solo si esta en estado pendiente
- Al confirmar un pedido se descuenta el stock de cada producto involucrado
- Al cancelar un pedido en estado confirmado o enviado, el stock se restituye
- Crear un pedido a partir del carrito: descuenta stock, vacia el carrito, deja el pedido en estado pendiente

## Autenticacion

- JWT con access token (expira en 2 horas), no guardar en localstorage
- Passwords hasheadas con bcrypt

## Requisitos

- Migraciones Alembic se ejecutan automaticamente al arrancar el backend
- Seed automatico e idempotente al arrancar si la base de datos esta vacia, que cree:
    - 1 administrador: [admin@quickshop.com](mailto:admin@quickshop.com) / Admin1234!
    - 2 clientes: [cliente1@quickshop.com](mailto:cliente1@quickshop.com) / Cliente1234! y [cliente2@quickshop.com](mailto:cliente2@quickshop.com) / Cliente1234!
    - 20 productos creados en base al fichero ubicado en docs/products-images.json
- CORS configurado en el backend para aceptar el origen del frontend
- Variables sensibles en archivos .env, con .env.example versionado y .env en .gitignore
- Ningun secreto, password o URL hardcodeado en el codigo fuente
- Frontend: Tendra header y un layout donde se muestren los componentes/layouts de cada pagina. Responsive

## Decisiones tecnicas

- **Backend**:
  - **Sin `passlib`**: Usar `bcrypt` directamente (`bcrypt.hashpw`/`checkpw`) por incompatibilidades.
  - **Email Validator**: Añadir `email-validator>=2.1.0` explícitamente para Pydantic `EmailStr`.
- **Frontend**:
  - **Sin PostCSS/Autoprefixer externos**: Configurar PostCSS inline en `vite.config.js` solo con `tailwindcss()` para evitar fallos de regex en Windows.
- **Docker & pnpm**:
  - **Node.js**: Usar `node:22-alpine` en frontend (pnpm 11 requiere Node >= 22.13).
  - **Instalación**: Copiar `pnpm-workspace.yaml` junto a lock/package antes de `pnpm install` en el Dockerfile.
  - **Builds no interactivos**: Declarar `allowBuilds` en `pnpm-workspace.yaml` (evita prompts de aprobación en agentes/CI).
  - **`.dockerignore` obligatorio**: Excluir `node_modules` y directorios temporales para evitar errores de symlinks en Windows.


## Tareas

Ejecutar en este orden estricto:

1. Identificar modulos del sistema. Los modulos son exactamente estos cinco:
    - autenticacion, usuarios, productos, carrito, pedidos
2. Crear docs/specs-prds/<modulo>.md para cada uno, conteniendo:
    - Descripcion del modulo
    - Modelo de datos (tablas, columnas, tipos, restricciones)
    - Endpoints (metodo, ruta, request, response, codigos de error)
    - Criterios de aceptacion
    - Pantallas en el frontend
3. Crear [CLAUDE.md](http://claude.md/) y [AGENTS.md](http://agents.md/) en la raiz con:
    - Convenciones generales
    - Estructura de carpetas
    - Orden de desarrollo: backend primero, frontend despues
    - Quiero que el CLAUDE.md haga referencia mediante progressive disclosure al AGENTS.md mediante el uso de la "@". Es decir, el contenido estara en AGENTS.md y en CLAUDE.md se referenciara al AGENTS.md
4. Crear backend/CLAUDE.md y backend/AGENTS.md con instrucciones especificas de backend
   - Quiero que el CLAUDE.md haga referencia mediante progressive disclosure al AGENTS.md mediante el uso de la "@".Es decir, el contenido estara en AGENTS.md y en CLAUDE.md se referenciara al AGENTS.md
5. Crear frontend/[CLAUDE.md](http://CLAUDE.md) y frontend/[AGENTS.md](http://AGENTS.md) con instrucciones especificas de frontend. 
   - Quiero que el CLAUDE.md haga referencia mediante progressive disclosure al AGENTS.md mediante el uso de la "@".Es decir, el contenido estara en AGENTS.md y en CLAUDE.md se referenciara al AGENTS.md
   - En el AGENTS.md y CLAUDE.md es importante esto (En pnpm 11 las aprobaciones de build scripts se guardan en pnpm-workspace.yaml (clave allowBuilds), no en el lockfile; el Dockerfile debe copiarlo antes  del install o fallará con ERR_PNPM_IGNORED_BUILDS.)
6. Integrar todo en docker-compose

## Convenciones de idioma y estilo

- Documentacion ([CLAUDE.md](http://claude.md/), [AGENTS.md](http://agents.md/), specs, README): castellano
- Sin emojis en ningun archivo del proyecto
