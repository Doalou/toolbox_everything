# Multi-stage build pour optimiser la taille
FROM python:3.12-slim AS builder

LABEL maintainer="toolbox-everything"
LABEL version="1.2"
LABEL description="Toolbox Everything - Une boîte à outils web complète"

# Installation des dépendances de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Création de l'environnement virtuel
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Image finale
FROM python:3.12-slim

LABEL maintainer="toolbox-everything"
LABEL version="1.2"
LABEL description="Toolbox Everything - Une boîte à outils web complète"
LABEL org.opencontainers.image.source="https://github.com/doalou/toolbox_everything"
LABEL org.opencontainers.image.documentation="https://github.com/doalou/toolbox_everything/README.md"

# Installation des dépendances runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libmagic1 \
    curl \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copie de l'environnement virtuel
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY . .

# Création des répertoires nécessaires
RUN mkdir -p uploads/temp uploads/temp_youtube downloads logs bin

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV DOCKER_ENV=1

EXPOSE 8000

# Création de l'utilisateur non-root
RUN groupadd -r toolbox && useradd -r -g toolbox toolbox
RUN chown -R toolbox:toolbox /app
USER toolbox

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--timeout", "900", "--access-logfile", "-", "--error-logfile", "-", "run:app"] 