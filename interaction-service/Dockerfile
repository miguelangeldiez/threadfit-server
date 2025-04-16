FROM python:3.13-alpine

# Instalar dependencias necesarias para compilar gevent y otros paquetes
RUN apk add --no-cache gcc musl-dev libffi-dev postgresql-dev python3-dev libev-dev linux-headers make file build-base 

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo requirements.txt
COPY requirements.txt .

# Actualizar pip y luego instalar las dependencias del proyecto
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos del proyecto
COPY . .

# Exponer el puerto de la aplicación
EXPOSE 5000

# Comando por defecto para ejecutar la aplicación
CMD ["python", "main.py"]
