# ── base ──────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

# HF Spaces expects port 7860
EXPOSE 7860

# ── system deps ───────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# ── workdir ───────────────────────────────────────────────────────────────────
WORKDIR /app

# ── python deps ───────────────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── copy source ───────────────────────────────────────────────────────────────
COPY environment/ ./environment/
COPY server/      ./server/
COPY openenv.yaml .
COPY inference.py .

# ── environment variables (override at runtime) ───────────────────────────────
ENV API_BASE_URL=https://api.openai.com/v1
ENV MODEL_NAME=gpt-4o-mini
ENV HF_TOKEN=""
ENV OPENAI_API_KEY=""

# ── healthcheck ───────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/health')"

# ── start server ──────────────────────────────────────────────────────────────
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "7860"]
