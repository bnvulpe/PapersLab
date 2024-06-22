#!/bin/bash

# Detener y desmontar los contenedores en el directorio /databases
echo "Stopping containers in /databases..."
cd ./databases || { echo "Directory /databases not found"; exit 1; }
docker compose down || { echo "Failed to run docker compose down in /databases"; exit 1; }

# Detener y desmontar los contenedores en el directorio /spark
echo "Stopping containers in /spark..."
cd ../spark || { echo "Directory /spark not found"; exit 1; }
docker compose down || { echo "Failed to run docker compose down in /spark"; exit 1; }

# Detener y desmontar los contenedores en el directorio raíz
echo "Stopping containers in the root directory..."
cd ../ || { echo "Failed to change directory to root"; exit 1; }
docker compose down || { echo "Failed to run docker compose down in root directory"; exit 1; }

# Eliminar el contenedor de configuración
cd docker-configuration || { echo "Directory /docker-configuration not found"; exit 1; }
docker rm docker_configuration || { echo "Failed to remove docker_configuration container"; exit 1; }

echo "All containers have been stopped and removed."
