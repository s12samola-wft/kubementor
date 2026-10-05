FROM python:3.12-slim

# Not pinned on purpose: we want Debian's latest security patch, and pinned
# apt versions are removed from the archive. Reproducibility comes from the
# pinned base image digest plus a Trivy scan on every build.
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends --only-upgrade libpcre2-8-0 \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/


RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.app:app"]