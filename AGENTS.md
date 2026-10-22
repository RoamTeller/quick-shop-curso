# QuickShop
- Aplicar los requisitos de openspec/changes/quickshop-inicial y conservar los artefactos del curso.
- Backend primero; frontend después. No ampliar el alcance sin indicarlo al usuario.
- Documentación e interfaz en castellano; código e identificadores en inglés. Sin emojis en archivos del proyecto.
- Backend: Python 3.11, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL 15 y uv.
- Frontend: React 18, Vite, Tailwind CSS 3 y React Router; dependencias con pnpm 11.
- Las transacciones y los permisos se verifican en backend; nunca confiar en el rol o precio enviados por el navegador.
- El stock se reserva al crear el pedido, una sola vez. Cualquier cancelación válida lo repone exactamente una vez.
- JWT solo en memoria del cliente, con expiración de dos horas e invalidación por versión de sesión.
- Credenciales y URLs mediante entorno. No leer, mostrar ni versionar .env; consultar .env.example.
- En pnpm 11 declarar allowBuilds en pnpm-workspace.yaml y copiarlo antes del install de Docker.
- No archivar cambios ni hacer commits o pushes sin solicitud del usuario.
- Pruebas: docker compose run --rm backend uv run pytest; docker compose run --rm frontend pnpm test; docker compose run --rm frontend pnpm build.

<!-- CODEGRAPH_START -->
## CodeGraph

Este proyecto está indexado con CodeGraph cuando existe `.codegraph/` en la raíz. Puede consultarse para explorar símbolos, dependencias y el impacto de los cambios:

- **MCP**, si está disponible: `codegraph_explore` devuelve código y relaciones entre símbolos. Incluye nombres de archivos o funciones concretos en la consulta.
- **Terminal**: `codegraph explore "<símbolos o pregunta>"` permite consultar el mismo índice, también desde subagentes como duplicate-finder.
- Comprueba los resultados contra el código actual cuando exista ambigüedad o el índice indique cambios pendientes. Las búsquedas y lecturas dirigidas siguen siendo válidas para verificar candidatos.

Si no existe `.codegraph/`, continúa sin CodeGraph; crear un índice requiere que el usuario lo solicite. El índice es local y no se versiona. La configuración MCP de este proyecto desactiva la telemetría de CodeGraph.
<!-- CODEGRAPH_END -->
