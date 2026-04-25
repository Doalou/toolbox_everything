# =====================================================
# Toolbox Everything — image Docker (multi-stage)
#
#   1. py-builder   : installe les deps Python dans /opt/venv
#   2. css-builder  : compile Tailwind (binaire Go standalone, pas de Node)
#   3. runtime      : image finale, zéro outil de build
# =====================================================
ARG APP_VERSION=1.3.1
ARG TAILWIND_VERSION=3.4.13

# -----------------------------------------------------
# 1) Build des deps Python
# -----------------------------------------------------
FROM python:3.12-slim AS py-builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------
# 2) Build du CSS Tailwind
#    Même pipeline que le dev local : script Python + CLI standalone.
#    Le binaire est téléchargé dans ce stage, puis jeté.
# -----------------------------------------------------
FROM python:3.12-slim AS css-builder

ARG TAILWIND_VERSION
ENV TAILWIND_VERSION=${TAILWIND_VERSION}

WORKDIR /build
COPY scripts/tailwind.py ./scripts/tailwind.py
COPY tailwind.config.js ./
COPY app/static/css/input.css ./app/static/css/input.css
COPY app/templates ./app/templates
COPY app/static/js ./app/static/js
COPY app/services ./app/services

RUN python scripts/tailwind.py build && \
    python scripts/tailwind.py check

# -----------------------------------------------------
# 3) Image finale
# -----------------------------------------------------
FROM python:3.12-slim

ARG APP_VERSION

LABEL maintainer="toolbox-everything"
LABEL version="${APP_VERSION}"
LABEL description="Toolbox Everything - Une boite a outils web complete"
LABEL org.opencontainers.image.source="https://github.com/doalou/toolbox_everything"
LABEL org.opencontainers.image.documentation="https://github.com/doalou/toolbox_everything/README.md"
LABEL org.opencontainers.image.version="${APP_VERSION}"

# libmagic retiré (plus utilisé). curl conservé pour le healthcheck Docker.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=py-builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY . .
# CSS Tailwind généré par le stage css-builder — écrase le .gitignore placeholder si présent
COPY --from=css-builder /build/app/static/css/tailwind.css /app/app/static/css/tailwind.css

# .env depuis env.example si absent, avec génération automatique de SECRET_KEY
RUN if [ ! -f .env ]; then cp env.example .env; fi && \
    SECRET=$(python -c "import secrets; print(secrets.token_hex(32))") && \
    sed -i "s/^SECRET_KEY=.*/SECRET_KEY=${SECRET}/" .env

RUN mkdir -p uploads/temp logs

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV DOCKER_ENV=1
ENV APP_VERSION=${APP_VERSION}

EXPOSE 8000

RUN groupadd -r toolbox && useradd -r -g toolbox toolbox
RUN chown -R toolbox:toolbox /app
USER toolbox

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--timeout", "900", "--access-logfile", "-", "--error-logfile", "-", "run:app"]
