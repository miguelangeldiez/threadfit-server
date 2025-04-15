# Auth Microservice 

Este es el microservicio de autenticación utilizando Flask, JWT y PostgreSQL. Demuestra cómo registrar usuarios (sign-up), autenticarlos (sign-in) y refrescar tokens (refresh) en un entorno contenedorizado con Docker Compose.

## Estructura del Proyecto

- **app.py:** Punto de entrada de la aplicación Flask.  
- **models.py:** Modelos de SQLAlchemy (en este caso, el modelo User).  
- **schemas.py:** Esquemas de Marshmallow para la serialización de objetos (por ejemplo, User).  
- **routes.py:** Endpoints de autenticación (sign-up, sign-in y refresh).  
- **config.py:** Configuración de la aplicación (conexión a la base de datos, JWT, etc.).  
- **requirements.txt:** Dependencias de Python.  
- **docker-compose.yml:** Configuración para levantar los contenedores de la aplicación y PostgreSQL.  
- **.env:** Archivo para definir variables de entorno (por ejemplo, credenciales de la base de datos).

## Configuración e Instrucciones

### 1. Prerrequisitos

- Tener instalado [Docker](https://www.docker.com/get-started) y [Docker Compose](https://docs.docker.com/compose/install/).
- (Opcional) Utilizar Postman, curl u otra herramienta para probar los endpoints.

### 2. Configurar Variables de Entorno

Crea un archivo **.env** en la raíz del proyecto con el siguiente contenido:

```env
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=auth_db
JWT_SECRET_KEY=a_very_secret_key
FLASK_APP=app.py
```

Estas variables se usarán tanto en el contenedor de PostgreSQL como en el de la aplicación.

### 3. Construir y Levantar los Contenedores

Utiliza Docker Compose para construir y ejecutar el proyecto:

```bash
docker-compose up --build
```

Esto levantará dos servicios:
- **db:** Contenedor con PostgreSQL (por defecto en el puerto 5432, o mapeado a otro puerto si así lo configuras).
- **app:** Contenedor con el microservicio Flask, expuesto en el puerto 5000.

### 4. Inicializar la Base de Datos

Con Flask-Migrate, genera y aplica las migraciones para crear las tablas en la base de datos. Ejecuta los siguientes comandos:

```bash
docker-compose run --rm app flask db init
docker-compose run --rm app flask db migrate -m "Initial migration"
docker-compose run --rm app flask db upgrade
```

Estos comandos crearán el directorio **migrations** en tu proyecto (gracias a los volúmenes, se persistirá en el host) y aplicarán los cambios a la base de datos.

## Cómo Probar los Endpoints

### 1. Registro de Usuario (Sign-Up)

Envía una solicitud POST al endpoint `/auth/sign-up` para registrar un nuevo usuario:

```bash
curl -X POST http://localhost:5000/auth/sign-up \
  -H "Content-Type: application/json" \
  -d '{"name": "usuario_test", "email": "test@example.com", "password": "secret"}'
```

Respuesta esperada (JSON):

```json
{
  "msg": "Usuario registrado con éxito"
}
```

### 2. Autenticación (Sign-In)

Para autenticar al usuario y obtener los tokens JWT, realiza una solicitud POST al endpoint `/auth/sign-in`:

```bash
curl -X POST http://localhost:5000/auth/sign-in \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "secret"}'
```

Respuesta esperada (JSON):

```json
{
  "access_token": "<access_token>",
  "refresh_token": "<refresh_token>",
  "user": {
    "id": "<user_id>",
    "username": "usuario_test"
  }
}
```

### 3. Refrescar el Token (Refresh)

Utiliza el token de refresco obtenido en el paso anterior para solicitar un nuevo token de acceso. Envía una solicitud POST al endpoint `/auth/refresh`:

```bash
curl -X POST http://localhost:5000/auth/refresh \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <refresh_token>"
```

Respuesta esperada (JSON):

```json
{
  "access_token": "<nuevo_access_token>"
}
```

## Limpieza

Para detener y remover los contenedores, ejecuta:

```bash
docker-compose down
```
