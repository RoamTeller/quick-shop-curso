# Carrito privado del cliente

## Descripción
Módulo carrito de QuickShop, conforme al cambio quickshop-inicial.

## Modelo de datos
Cart: id y user_id único. CartItem: id, cart_id, product_id, quantity > 0; restricción única (cart_id,product_id). Total calculado con precios actuales del servidor.

## API y errores
- GET /api/cart: carrito propio con artículos, subtotales y total; 200.
- POST /api/cart/items: {product_id,quantity}; acumula cantidad; 200, 404 o 409 por stock.
- PATCH /api/cart/items/{product_id}: {quantity}; establece cantidad; 200, 404 o 409.
- DELETE /api/cart/items/{product_id}: elimina artículo propio; 204 o 404.
- DELETE /api/cart: vacía el carrito propio; 204.
- 401 para credenciales ausentes, expiradas o revocadas; 403 para un rol no autorizado.

## Criterios de aceptación y pantallas
- Cantidad positiva y nunca superior al stock disponible; validar sumas y modificaciones.
- El administrador no tiene carrito: 403.
- No modificar stock hasta confirmar la compra creando el pedido.
- No mostrar ni modificar carritos ajenos.
- Pantalla de carrito con controles de cantidad, eliminación, total y creación del pedido.
