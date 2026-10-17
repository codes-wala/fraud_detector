# syntax=docker/dockerfile:1
# ---------- base: runtime dependencies + application code ----------
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements-prod.txt .
RUN pip install -r requirements-prod.txt

COPY fraud_detector/ fraud_detector/
COPY templates/ templates/
COPY wsgi.py run.py ./

# ---------- test: adds dev tools and runs the 101-test suite ----------
# Build with:  docker build --target test -t fraudguard:test .
FROM base AS test
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY tests/ tests/
COPY mutation_test.py analysis_extra.py ./
RUN mkdir -p results
CMD ["python", "-m", "pytest", "-q"]

# ---------- runtime: default final image ----------
FROM base AS runtime

LABEL org.opencontainers.image.title="FraudGuard" \
      org.opencontainers.image.description="AI-based fraud detection prototype (Flask + scikit-learn, synthetic data only)"

RUN useradd --create-home --uid 10001 appuser
USER appuser

ENV PORT=5000
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,os; urllib.request.urlopen('http://127.0.0.1:%s/api/health' % os.environ.get('PORT','5000'), timeout=3)"

# The model trains on synthetic data at start-up, so keep workers few.
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT} --workers 2 --timeout 60 --access-logfile - wsgi:app"]
