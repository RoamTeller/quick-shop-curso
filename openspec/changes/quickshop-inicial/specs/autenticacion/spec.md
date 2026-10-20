# Especificación: autenticación

## ADDED Requirements

### Requirement: Inicio de sesión
El sistema SHALL cumplir el siguiente requisito: El sistema debe permitir iniciar sesión con email y contraseña y devolver un JWT con expiración de dos horas.

#### Scenario: Inicio de sesión
- **WHEN** un usuario presenta credenciales válidas
- **THEN** recibe un JWT con expiración de dos horas

### Requirement: Hash de contraseña
El sistema SHALL cumplir el siguiente requisito: Las contraseñas deben almacenarse únicamente con hash bcrypt.

#### Scenario: Hash de contraseña
- **WHEN** se almacena una contraseña
- **THEN** se guarda únicamente su hash bcrypt

### Requirement: Autorización por rol
El sistema SHALL cumplir el siguiente requisito: El sistema debe distinguir los roles `cliente` y `administrador` y rechazar operaciones no autorizadas con 401/403.

#### Scenario: Autorización por rol
- **WHEN** una petición no tiene sesión válida o requiere otro rol
- **THEN** se rechaza con 401 o 403 respectivamente

### Requirement: Persistencia del token
El sistema SHALL cumplir el siguiente requisito: El token no debe persistirse en localStorage.

#### Scenario: Persistencia del token
- **WHEN** un usuario inicia sesión
- **THEN** el token se mantiene en memoria y no se guarda en localStorage

### Requirement: Respuesta privada de recuperación
El sistema SHALL cumplir el siguiente requisito: El sistema debe permitir solicitar recuperación de contraseña mediante email sin revelar si la dirección está registrada.

#### Scenario: Respuesta privada de recuperación
- **WHEN** se solicita recuperar una dirección registrada o no registrada
- **THEN** se devuelve la misma respuesta pública

### Requirement: Token de recuperación
El sistema SHALL cumplir el siguiente requisito: La solicitud debe generar un token aleatorio, de un solo uso, con expiración limitada y almacenado de forma segura.

#### Scenario: Token de recuperación
- **WHEN** un usuario registrado solicita recuperación
- **THEN** recibe un token aleatorio de un solo uso y expiración limitada que se almacena de forma segura

### Requirement: Restablecimiento válido
El sistema SHALL cumplir el siguiente requisito: El usuario debe poder establecer una nueva contraseña con un token válido; los tokens anteriores deben quedar invalidados.

#### Scenario: Restablecimiento válido
- **WHEN** un usuario presenta un token válido y una contraseña aceptable
- **THEN** se actualiza la contraseña y se invalidan los tokens de recuperación anteriores

### Requirement: Revocación de sesiones
El sistema SHALL cumplir el siguiente requisito: Tras cambiar la contraseña deben invalidarse las sesiones o tokens activos del usuario.

#### Scenario: Revocación de sesiones
- **WHEN** se cambia la contraseña
- **THEN** los tokens y sesiones activos anteriores dejan de dar acceso

### Requirement: Validación de nueva contraseña
El sistema SHALL cumplir el siguiente requisito: La nueva contraseña debe cumplir las mismas reglas de seguridad y almacenarse con bcrypt.

#### Scenario: Validación de nueva contraseña
- **WHEN** se intenta restablecer una contraseña que incumple las reglas
- **THEN** se rechaza el cambio; una contraseña aceptada se almacena con bcrypt
