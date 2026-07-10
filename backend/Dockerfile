# syntax=docker/dockerfile:1

# AZI Backend — production image for Fly.io / Cloud Run
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# Install deps first so this layer is cached when only app code changes.
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# App code.
COPY . .

EXPOSE 8080

# Bind to 0.0.0.0 and the port Fly provides (defaults to 8080).
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
