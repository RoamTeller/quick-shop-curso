# Catálogo y administración

## Descripción
Módulo productos de QuickShop, conforme al cambio quickshop-inicial.

## Modelo de datos
Product: id, name, description, price Numeric(10,2) positivo, stock entero >= 0, image_url, is_active y timestamps.

## API y errores
- GET /api/products: catálogo de productos activos; 200.
- GET /api/products/{id}: detalle activo; 200 o 404.
- GET /api/admin/products: catálogo completo para administrador; 200 o 403.
- POST /api/admin/products: {name,description,price,stock,image_url,is_active}; 201; 422 para datos inválidos.
- PUT /api/admin/products/{id}: mismos campos; 200 o 404.
- DELETE /api/admin/products/{id}: desactivación lógica; 204.
- 401 para credenciales ausentes, expiradas o revocadas; 403 para un rol no autorizado.

## Criterios de aceptación y pantallas
- Seed de exactamente 20 productos desde docs/products-images.json en una base vacía, sin duplicarlos al reiniciar.
- Precio decimal enviado como cadena y validado con dos decimales; nunca aceptar precio desde carrito o checkout.
- Producto sin stock visible con botón de agregar deshabilitado.
- Solo administradores crean, editan y desactivan.
- Pantallas de catálogo, detalle y administración con formulario.
