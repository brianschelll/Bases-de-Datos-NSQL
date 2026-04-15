FROM python:3.10-slim

WORKDIR /app

# Copiamos e instalamos los requerimientos primero (buena práctica de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Exponemos el puerto 3000 (el mismo que pusimos en el docker-compose)
EXPOSE 3000

# Comando para arrancar el servidor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]