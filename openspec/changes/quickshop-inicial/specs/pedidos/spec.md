# Especificación: pedidos

## ADDED Requirements

### Requirement: Creación desde carrito
El sistema SHALL cumplir el siguiente requisito: Un cliente puede crear un pedido desde su carrito; se descuenta stock, se vacía el carrito y el pedido nace como `pendiente`.

#### Scenario: Creación desde carrito
- **WHEN** un cliente confirma un carrito con stock disponible
- **THEN** se crea un pedido pendiente, se descuenta stock una sola vez y se vacía el carrito

### Requirement: Permisos de transición
El sistema SHALL cumplir el siguiente requisito: Solo el administrador puede cambiar estados, salvo que el cliente cancele su propio pedido en estado `pendiente`.

#### Scenario: Permisos de transición
- **WHEN** un cliente cancela su propio pedido pendiente
- **THEN** se cancela; otros cambios de estado se reservan al administrador

### Requirement: Restitución de stock
El sistema SHALL cumplir el siguiente requisito: Al cancelar un pedido `confirmado` o `enviado`, el stock debe restituirse.

#### Scenario: Restitución de stock
- **WHEN** un administrador cancela un pedido confirmado o enviado
- **THEN** se restituye el stock una sola vez

### Requirement: Privacidad de pedidos
El sistema SHALL cumplir el siguiente requisito: Un cliente solo puede consultar sus propios pedidos; el administrador puede gestionarlos todos.

#### Scenario: Privacidad de pedidos
- **WHEN** un cliente consulta sus pedidos
- **THEN** solo puede ver los propios; un administrador puede gestionarlos todos
