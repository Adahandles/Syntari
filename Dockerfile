# Syntari Programming Language - Production Dockerfile
# Multi-stage build for minimal image size

# Stage 1: Builder
FROM python:3.12-slim as builder

LABEL org.opencontainers.image.title="Syntari" \
      org.opencontainers.image.description="AI-integrated programming language" \
      org.opencontainers.image.version="0.4.0" \
      org.opencontainers.image.vendor="DeuOS, LLC" \
      org.opencontainers.image.source="https://github.com/Adahandles/Syntari"

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt pyproject.toml ./
COPY src/ ./src/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 syntari && \
    chown -R syntari:syntari /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=syntari:syntari . .

# Switch to non-root user
USER syntari

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SYNTARI_HOME=/app \
    PATH="/app:${PATH}"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)" || exit 1

# Default command (REPL)
ENTRYPOINT ["python3", "main.py"]
CMD ["--repl"]

# Expose port for Web REPL (if needed)
EXPOSE 8765

# Volume for user scripts
VOLUME ["/scripts"]

# Labels for runtime
LABEL maintainer="legal@deuos.io" \
      version="0.4.0" \
      description="Syntari programming language runtime"
