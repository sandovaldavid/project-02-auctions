FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "tu_proyecto.wsgi:application"]
