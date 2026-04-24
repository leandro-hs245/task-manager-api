FROM python:3.12-slim

WORKDIR /app

ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY pyproject.toml README.md ./
COPY app ./app

EXPOSE 8000

CMD ["python", "-c", "print('Wire uvicorn to app.adapters.input.api.main:app when FastAPI is added.')"]
