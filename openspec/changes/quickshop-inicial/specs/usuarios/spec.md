# Especificación: usuarios

## ADDED Requirements

### Requirement: Datos y unicidad
El sistema SHALL cumplir el siguiente requisito: Un usuario debe tener id, email único, hash de contraseña, rol y marcas de creación/actualización.

#### Scenario: Datos y unicidad
- **WHEN** se intenta registrar un email existente
- **THEN** se rechaza el duplicado y se conserva el usuario anterior

### Requirement: Seed idempotente
El sistema SHALL cumplir el siguiente requisito: El seed debe crear un administrador y dos clientes de forma idempotente.

#### Scenario: Seed idempotente
- **WHEN** se ejecuta el seed varias veces
- **THEN** se conservan un administrador y dos clientes iniciales sin duplicarlos

### Requirement: Perfil privado
El sistema SHALL cumplir el siguiente requisito: Un cliente autenticado debe poder consultar su perfil sin acceder a datos de otros usuarios.

#### Scenario: Perfil privado
- **WHEN** un cliente autenticado solicita su perfil
- **THEN** recibe únicamente sus datos y nunca el hash de contraseña
