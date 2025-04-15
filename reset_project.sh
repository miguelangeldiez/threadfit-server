#!/bin/bash

# íº« Parar y eliminar contenedores + volÃºmenes
echo "í·¹ Apagando servicios y limpiando volÃºmenes..."
docker-compose down -v

# í·¨ Borrar carpetas de migraciones
echo "í·‘ Borrando migraciones de microservicios..."
rm -rf auth-service/migrations/
rm -rf post-service/migrations/
rm -rf data-service/migrations/
rm -rf interaction-service/migrations/
rm -rf user-service/migrations/

# íº€ Reconstruir y levantar servicios
echo "í´§ Reconstruyendo contenedores..."
docker-compose up -d --build

sleep 5  # Esperar a que los contenedores estÃ©n estables

# í»  Migraciones para auth-service
echo "í³¦ Aplicando migraciones en auth-service..."
docker exec auth-service flask db init
docker exec auth-service flask db migrate -m "Initial migration"
docker exec auth-service flask db upgrade

# í»  Migraciones para post-service
echo "í³¦ Aplicando migraciones en post-service..."
docker exec post-service flask db init
docker exec post-service flask db migrate -m "Initial migration"
docker exec post-service flask db upgrade

# í»  Migraciones para data-service
echo "í³¦ Aplicando migraciones en data-service..."
docker exec data-service flask db init
docker exec data-service flask db migrate -m "Initial migration"
docker exec data-service flask db upgrade

# í»  Migraciones para interaction-service
echo "í³¦ Aplicando migraciones en interaction-service..."
docker exec interaction-service flask db init
docker exec interaction-service flask db migrate -m "Initial migration"
docker exec interaction-service flask db upgrade

# í»  Migraciones para user-service
echo "í³¦ Aplicando migraciones en user-service..."
docker exec user-service flask db init
docker exec user-service flask db migrate -m "Initial migration"
docker exec user-service flask db upgrade

# âœ… Mostrar estado final
echo "âœ… Contenedores en ejecuciÃ³n:"
docker ps
