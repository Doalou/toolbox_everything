# Multi-stage build pour optimiser la taille de l'image
FROM python:3.12-slim AS builder

# Métadonnées de l'image
LABEL maintainer="toolbox-everything"
LABEL version="1.1.2c"
LABEL description="Toolbox Everything - Une boîte à outils web complète avec téléchargeur YouTube et convertisseur de médias"

# Installation des dépendances de build avec correctifs de sécurité
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

# Métadonnées de l'image finale
LABEL maintainer="toolbox-everything"
LABEL version="1.1.2c"
LABEL description="Toolbox Everything - Une boîte à outils web complète"
LABEL org.opencontainers.image.source="https://github.com/doalou/toolbox_everything"
LABEL org.opencontainers.image.documentation="https://github.com/doalou/toolbox_everything/README.md"

# Installation des dépendances runtime avec correctifs de sécurité
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libmagic1 \
    curl \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copie de l'environnement virtuel depuis le builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Configuration du répertoire de travail
WORKDIR /app

# Copie du code source
COPY . .

# Création des répertoires nécessaires
RUN mkdir -p uploads/temp uploads/temp_youtube downloads logs bin

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Port exposé
EXPOSE 8000

# Création de l'utilisateur non-root pour la sécurité
RUN groupadd -r toolbox && useradd -r -g toolbox toolbox
RUN chown -R toolbox:toolbox /app
USER toolbox

# Commande par défaut
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--access-logfile", "-", "--error-logfile", "-", "run:app"] 