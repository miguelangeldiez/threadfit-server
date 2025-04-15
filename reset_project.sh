#!/bin/bash

# � Parar y eliminar contenedores + volúmenes
echo "� Apagando servicios y limpiando volúmenes..."
docker-compose down -v

# � Borrar carpetas de migraciones
echo "� Borrando migraciones de microservicios..."
rm -rf auth-service/migrations/
rm -rf post-service/migrations/
rm -rf data-service/migrations/
rm -rf interaction-service/migrations/
rm -rf user-service/migrations/

# � Reconstruir y levantar servicios
echo "� Reconstruyendo contenedores..."
docker-compose up -d --build

sleep 5  # Esperar a que los contenedores estén estables

# � Migraciones para auth-service
echo "� Aplicando migraciones en auth-service..."
docker exec auth-service flask db init
docker exec auth-service flask db migrate -m "Initial migration"
docker exec auth-service flask db upgrade

# � Migraciones para post-service
echo "� Aplicando migraciones en post-service..."
docker exec post-service flask db init
docker exec post-service flask db migrate -m "Initial migration"
docker exec post-service flask db upgrade

# � Migraciones para data-service
echo "� Aplicando migraciones en data-service..."
docker exec data-service flask db init
docker exec data-service flask db migrate -m "Initial migration"
docker exec data-service flask db upgrade

# � Migraciones para interaction-service
echo "� Aplicando migraciones en interaction-service..."
docker exec interaction-service flask db init
docker exec interaction-service flask db migrate -m "Initial migration"
docker exec interaction-service flask db upgrade

# � Migraciones para user-service
echo "� Aplicando migraciones en user-service..."
docker exec user-service flask db init
docker exec user-service flask db migrate -m "Initial migration"
docker exec user-service flask db upgrade

# ✅ Mostrar estado final
echo "✅ Contenedores en ejecución:"
docker ps
