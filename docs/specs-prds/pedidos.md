# Compra y gestión de pedidos

## Descripción
Módulo pedidos de QuickShop, conforme al cambio quickshop-inicial.

## Modelo de datos
Order: id, user_id, status, total, created_at y updated_at. OrderItem: pedido, product_id opcional, snapshot de nombre, precio unitario y cantidad. Estados pendiente, confirmado, enviado, entregado, cancelado.

## API y errores
- POST /api/orders: crea desde carrito propio, sin precios enviados por cliente; 201; 409 por carrito vacío o falta de stock.
- GET /api/orders: pedidos propios; administrador ve todos; 200.
- GET /api/orders/{id}: detalle autorizado; 200 o 404.
- POST /api/orders/{id}/cancel: cliente propietario si pendiente; administrador si pendiente/confirmado/enviado; 200 o 409.
- PATCH /api/admin/orders/{id}/status: {status}; administrador; 200 o 409.
- 401 para credenciales ausentes, expiradas o revocadas; 403 para un rol no autorizado.

## Criterios de aceptación y pantallas
- La creación bloquea carrito y productos, descuenta stock una vez, guarda precios, vacía carrito y crea pedido pendiente dentro de una transacción.
- Confirmar y enviar no vuelven a descontar stock; prevalece la especificación de creación del cambio sobre la contradicción del prompt inicial.
- Cancelación válida repone stock una sola vez, también para pedidos pendientes que ya lo reservaron.
- Transiciones: pendiente a confirmado/cancelado; confirmado a enviado/cancelado; enviado a entregado/cancelado. Estados finales no permiten cambios.
- Un cliente solo ve y cancela sus pedidos pendientes; administrador gestiona todos.
- Pantallas de historial, detalle y administración de estados.
