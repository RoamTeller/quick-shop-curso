# Especificación: carrito

## ADDED Requirements

### Requirement: Gestión del carrito
El sistema SHALL cumplir el siguiente requisito: Un cliente puede agregar, modificar, eliminar artículos y vaciar su carrito.

#### Scenario: Gestión del carrito
- **WHEN** un cliente agrega, modifica, elimina artículos o vacía su carrito
- **THEN** se aplica el cambio a su carrito

### Requirement: Cantidad válida
El sistema SHALL cumplir el siguiente requisito: La cantidad debe ser positiva y nunca superar el stock disponible.

#### Scenario: Cantidad válida
- **WHEN** se solicita una cantidad no positiva o superior al stock
- **THEN** se rechaza el cambio sin modificar el carrito

### Requirement: Carrito exclusivo de clientes
El sistema SHALL cumplir el siguiente requisito: El administrador no debe disponer de carrito.

#### Scenario: Carrito exclusivo de clientes
- **WHEN** un administrador solicita un carrito
- **THEN** la operación se rechaza con 403

### Requirement: Propietario del carrito
El sistema SHALL cumplir el siguiente requisito: El carrito debe pertenecer exclusivamente al cliente autenticado.

#### Scenario: Propietario del carrito
- **WHEN** un cliente consulta su carrito
- **THEN** solo obtiene los artículos de su propio carrito
