# Especificación: productos

## ADDED Requirements

### Requirement: Datos del producto
El sistema SHALL cumplir el siguiente requisito: Un producto debe tener nombre, descripción, precio decimal positivo con dos decimales, stock entero no negativo, URL de imagen e indicador `is_active`.

#### Scenario: Datos del producto
- **WHEN** se intenta guardar un producto con precio no positivo o stock negativo
- **THEN** se rechazan los datos

### Requirement: Catálogo inicial
El sistema SHALL cumplir el siguiente requisito: El catálogo debe incluir 20 productos del fichero `docs/products-images.json`.

#### Scenario: Catálogo inicial
- **WHEN** se inicializa una base vacía
- **THEN** se crean los 20 productos del fichero del curso

### Requirement: Producto agotado
El sistema SHALL cumplir el siguiente requisito: Los productos sin stock deben ser visibles, pero no agregables al carrito.

#### Scenario: Producto agotado
- **WHEN** se consulta un producto sin stock
- **THEN** sigue visible y no se permite añadirlo al carrito

### Requirement: Gestión administrativa
El sistema SHALL cumplir el siguiente requisito: Solo el administrador puede crear, editar o desactivar productos.

#### Scenario: Gestión administrativa
- **WHEN** un cliente intenta crear, editar o desactivar un producto
- **THEN** se rechaza con 403; un administrador sí puede realizar la operación
