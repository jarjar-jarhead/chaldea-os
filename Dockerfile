
FROM python:3.12-slim

# Prevent Python from buffering stdout/stderr (ensures instant terminal logs)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create and use an isolated app directory
WORKDIR /app

# Install dependencies in a cached layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project (code, templates, and pre-seeded db.sqlite3)
COPY . .

# Pre-compile and compress static assets for WhiteNoise
RUN python manage.py collectstatic --noinput

# Document the port the container listens on
EXPOSE 8000

# Start Gunicorn with 2 worker processes binding to all interfaces
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]