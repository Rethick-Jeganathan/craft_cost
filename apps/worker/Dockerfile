FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
COPY worker ./worker
RUN useradd -m -u 10001 appuser && chown -R appuser:appuser /app
USER appuser
CMD ["python", "-m", "worker.main"]
