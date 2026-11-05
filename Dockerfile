FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./
# requirements-dev incluye pytest/cov/httpx para el servicio "tests" de compose
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

# Render/Railway/Fly inyectan $PORT; en local usa 8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
