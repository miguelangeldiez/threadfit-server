# ThreadFit Backend

Este es el servidor para la aplicación **ThreadFit**, una red social enfocada en deportes y salud. El servidor proporciona APIs REST y soporte para WebSockets para funcionalidades en tiempo real como "Me gusta" en las publicaciones.

---

## **Características**

- **Autenticación JWT**: Protección de rutas y manejo de sesiones.
- **Base de datos PostgreSQL**: Gestión de usuarios, publicaciones, "Me gusta" y comentarios.
- **WebSockets**: Soporte en tiempo real para eventos como "Me gusta".
- **CORS habilitado**: Permite solicitudes desde el cliente alojado en un dominio diferente.
- **Escalabilidad**: Preparado para ser desplegado en entornos de contenedores como Kubernetes.

---

## **Requisitos previos**

- **Python 3.8 o superior**
- **Pipenv o virtualenv** (opcional, recomendado para aislamiento del entorno)

---

## **Instalación**

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/threadfit-backend.git
   cd threadfit-backend
