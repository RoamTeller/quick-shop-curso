# Revisión de duplicados: quickshop-inicial

Fecha: 22 de octubre de 2026.

Revisión realizada por el subagente local duplicate-finder. Informe guardado por el agente principal.

## Resultado

Se identificaron **tres grupos de duplicación relevantes para mantenimiento**. No se ha demostrado que produzcan fallos funcionales en la versión revisada. Las propuestas son recomendaciones: no se ha modificado el código ni se han aplicado refactorizaciones.

## Alcance, método y limitaciones

Se revisó el código de aplicación actual de backend/app y frontend/src: HEAD 6a5b418 y la corrección local de mensajes de validación en frontend/src/api.js. Se consultó frontend/src/App.test.jsx y las pruebas de backend para valorar las recomendaciones. La revisión incluye código ya existente de quickshop-inicial; los hallazgos no se atribuyen a cambios realizados en este turno ni se limitan al diff pendiente.

Se siguieron .codex/agents/duplicate-finder.toml y los AGENTS.md aplicables. El subagente delimitó los archivos mediante rg --files, buscó responsabilidades repetidas y contrastó manualmente las apariciones, usos, permisos y efectos secundarios. El agente principal comprobó las ubicaciones de los tres grupos y las pruebas mencionadas antes de guardar este informe.

No se instalaron herramientas, ejecutaron pruebas, leyeron archivos .env ni usaron servicios externos durante la revisión. Se excluyeron dependencias, archivos generados, migraciones, documentación y configuración de skills y agentes como candidatos. No se calcula un porcentaje de duplicación ni se afirma cobertura exhaustiva. La consulta estática de pruebas existentes no acredita que una futura refactorización las supere.

Todas las rutas y líneas siguientes se refieren a la versión inspeccionada y son relativas a la raíz de QuickShop.

## 1. Consulta y bloqueo de productos en compra y cancelación

**Prioridad de mantenimiento: media. Confianza: alta.**

Apariciones:

- backend/app/commerce.py:123–124, función checkout.
- backend/app/commerce.py:164–165, función cancel.

Ambos bloques extraen y ordenan los identificadores de producto, ejecutan la misma consulta y construyen un diccionario por Product.id:

```python
select(Product).where(Product.id.in_(ids)).order_by(Product.id).with_for_update().execution_options(populate_existing=True)
```

El origen de los identificadores cambia de cart.items a order.items.

**Diferencias que hay que conservar:** checkout comprueba disponibilidad, reserva stock y guarda precios; cancel repone cantidades previamente reservadas. La compra bloquea antes al propietario del carrito y la cancelación bloquea antes el pedido. Esos bloqueos y el resto de cada operación deben permanecer en sus flujos.

**Impacto:** un cambio en el bloqueo o refresco de productos exige mantener dos copias. Una divergencia podría afectar a la concurrencia del stock; no se observó tal divergencia en esta revisión.

**Consolidación mínima sugerida:** extraer lock_products_by_ids(db, ids), manteniendo ordenación, consulta y diccionario. Dejar fuera del helper comprobaciones, descuentos, reposiciones y bloqueos previos. No filtrar por is_active: una cancelación debe poder reponer stock de un producto desactivado.

**Validación si se implementa:**

- Conservar test_competing_checkouts_cannot_oversell.
- Conservar test_duplicate_checkout_same_cart_only_one_order.
- Conservar test_checkout_rolls_back_every_product_if_stock_changes.
- Conservar test_cancellation_restores_once.
- Añadir cancelación de un pedido cuyo producto se desactivó después de comprar.
- Añadir compra y cancelación concurrentes con varios productos compartidos, verificando stock final y ausencia de interbloqueos.

## 2. Adición al carrito en catálogo y detalle

**Prioridad de mantenimiento: media. Confianza: alta.**

Apariciones:

- frontend/src/App.jsx:210–224, función Catalog.add; petición y notificación en 215–223.
- frontend/src/App.jsx:434–450, manejador del botón de ProductDetail; petición y notificación en 441–449.

Ambas implementaciones comprueban la sesión, usan action.run, realizan POST /cart/items con token, identificador y cantidad 1, emiten cart-updated y notifican éxito.

**Diferencias que hay que conservar:** el catálogo usa product.id; el detalle convierte el parámetro de ruta con Number(id). El detalle conserva state.from para volver después de iniciar sesión; el catálogo abre /acceso sin ese destino. Los mensajes de éxito y estados de operación de cada pantalla son distintos. La diferencia de retorno puede ser deliberada: no debe cambiarse implícitamente al consolidar.

**Impacto:** cambiar el contrato de adición, la actualización del contador o el tratamiento de éxito requiere modificar ambas implementaciones.

**Consolidación mínima sugerida:** un hook useAddToCart que reutilice useAction, haga la petición y emita cart-updated únicamente tras el éxito. Parametrizar destino de acceso y mensaje cuando sea necesario. Mantener estados de operación independientes y evitar un hook genérico para todas las mutaciones.

CartPage.change, en frontend/src/App.jsx:658–664, comparte parte del patrón pero además recarga recursos y maneja operaciones distintas; no conviene incluirlo forzosamente en la abstracción.

**Validación si se implementa:**

- Conservar las pruebas de productos agotados y sesión sin persistencia del token.
- Probar adición desde catálogo y detalle: una petición con el identificador correcto y cantidad 1.
- Probar doble clic mientras la respuesta sigue pendiente.
- Probar rechazo 409: error visible sin notificación de éxito ni evento de actualización.
- Probar el destino tras el acceso de visitantes en ambas pantallas.
- Probar actualización del contador del encabezado después del éxito.

Las pruebas de interfaz consultadas no ejercitan directamente ambos flujos de adición.

## 3. Invalidación de enlaces de recuperación

**Prioridad de mantenimiento: baja. Confianza: alta.**

Apariciones:

- backend/app/auth.py:18–20, función invalidate_sessions.
- backend/app/auth.py:54–56, función forgot.

Ambos ejecutan un UPDATE sobre PasswordReset filtrando por user_id y used_at IS NULL y asignando la hora actual a used_at.

**Diferencias que hay que conservar:** invalidate_sessions incrementa además user.token_version después de cambiar o restablecer la contraseña. forgot solo debe invalidar enlaces anteriores y emitir uno nuevo. Solicitar el correo no debe cerrar sesiones existentes.

**Impacto:** cambiar qué enlaces se invalidan obliga a mantener ambas consultas. Reutilizar directamente invalidate_sessions en forgot introduciría una revocación de sesiones no prevista.

**Consolidación mínima sugerida:** extraer solo invalidate_reset_tokens(db, user_id, now). Mantener el incremento de versión en invalidate_sessions. El parámetro now permite que forgot use el mismo instante para invalidar enlaces anteriores y calcular la caducidad del nuevo.

**Validación si se implementa:**

- Conservar test_new_recovery_invalidates_previous_token.
- Conservar test_reset_revokes_sessions_and_single_use.
- Conservar test_change_password_requires_current_and_revokes_all.
- Conservar test_simultaneous_reset_only_one_succeeds.
- Añadir una prueba explícita de que solicitar recuperación mantiene válida la sesión hasta que se cambia la contraseña.

## Repeticiones deliberadas y candidatos descartados

- Estados de pedido: frontend/src/App.jsx:854–858 y backend/app/commerce.py:182 comparten transiciones. El navegador decide qué acciones mostrar y el servidor valida permisos y transiciones. Mantener la validación del servidor y comprobar coherencia mediante pruebas.
- Validación en navegador y servidor: los formularios, mensajes de frontend/src/api.js y esquemas de backend/app/schemas.py tienen responsabilidades diferentes. La corrección local del mensaje no justifica otra abstracción.
- Cambio y restablecimiento de contraseña: reset y change_password ya comparten invalidate_sessions; sus verificaciones previas son distintas. No se propone agrupar los endpoints.
- Carrito y pedido: el carrito usa precio y disponibilidad actuales y el pedido una instantánea histórica. No conviene unificar modelos o cálculos ocultando esa diferencia.
- CSS y JSX: se descartaron coincidencias pequeñas de maquetación, atributos, botones, etiquetas y reglas habituales del framework.

## Siguiente paso recomendado

Priorizar el helper de bloqueo de productos y la operación de adición al carrito. La extracción de invalidación de enlaces es pequeña y opcional. Cualquier refactorización debe preservar permisos, transacciones, orden de bloqueos y efectos secundarios, y verificarse con las pruebas indicadas.

Este informe no aplica cambios de código, no añade tareas de OpenSpec y no realiza commits, pushes ni archivado.
