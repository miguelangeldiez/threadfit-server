FROM python:3.13-alpine

# Instala las dependencias necesarias del sistema
RUN apk add --no-cache gcc musl-dev libffi-dev postgresql-dev python3-dev libev-dev linux-headers make file

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
