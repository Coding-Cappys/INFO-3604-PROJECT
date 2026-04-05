FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/pyproject.toml

RUN pip install --no-cache-dir \
    "email-validator>=2.3.0" \
    "flask>=3.1.3" \
    "flask-login>=0.6.3" \
    "flask-sqlalchemy>=3.1.1" \
    "flask-wtf>=1.2.2" \
    "gunicorn>=25.3.0" \
    "pillow>=12.1.1" \
    "psycopg2-binary>=2.9.11" \
    "python-dotenv>=1.2.2" \
    "qrcode[pil]>=8.2" \
    "werkzeug>=3.1.7" \
    "wtforms>=3.2.1"

COPY artifacts/uwi-festival /app/artifacts/uwi-festival

RUN mkdir -p /app/data

EXPOSE 5000

CMD ["sh", "-c", "gunicorn --chdir artifacts/uwi-festival --bind 0.0.0.0:${PORT:-5000} wsgi:app"]
