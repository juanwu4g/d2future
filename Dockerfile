# syntax=docker/dockerfile:1

# ----------------------------------------------------------------------------
# Stage 1 — builder: install runtime dependencies into an isolated venv.
# Kept separate so build tooling never reaches the final image.
# ----------------------------------------------------------------------------
FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Copy ONLY requirements first so this layer (and the pip install below) stays
# cached when application code changes but dependencies do not.
COPY requirements.txt .

RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ----------------------------------------------------------------------------
# Stage 2 — final: slim runtime with the venv copied in and a non-root user.
# ----------------------------------------------------------------------------
FROM python:3.12-slim AS final

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Create an unprivileged user to run the app.
RUN useradd --create-home --uid 10001 appuser

WORKDIR /app

# Bring over the pre-built virtual environment from the builder stage.
COPY --from=builder /opt/venv /opt/venv

# Copy application code last — the most frequently changed layer.
COPY src/ ./src/

USER appuser

EXPOSE 8080

# Liveness check using only the Python stdlib (no curl needed on slim).
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8080/health').status==200 else 1)"

WORKDIR /app/src
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
