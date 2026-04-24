# Toolbox Everything

Boîte à outils web modulaire — téléchargement YouTube, conversion média, outils utilitaires (QR, hash, JSON, passwords…) et **150+ opérations PDF** via Stirling PDF embarqué.

Interface responsive Flask + Tailwind, le tout conteneurisé et prêt pour la prod.

**Version actuelle : 1.3.0**

---

## Fonctionnalités

| Module | Description |
|--------|-------------|
| **YouTube Downloader** | Vidéo / audio via `yt-dlp` 2026.x, téléchargement parallèle des fragments, formats `bestvideo+bestaudio` mergés par FFmpeg |
| **Convertisseur Média** | Images (PNG, JPG, WebP, GIF…) et vidéos (MP4, WebM, MKV…) avec contrôle de qualité (CRF FFmpeg) |
| **Outils Essentiels** | QR codes, mots de passe, hashes, Base64, JSON formatter, palettes couleurs, timestamps, raccourcisseur d'URL |
| **Outils PDF** | 150+ opérations PDF (fusion, split, OCR, compression, conversion, signature, watermark…) via Stirling PDF embarqué — **mode amnésique** : `/configs`, `/logs` et `/tmp` en tmpfs (RAM), aucune analytics, nettoyage temp agressif (1h / 5min) |
| **Healthcheck** | Endpoint `/health` avec statut de `yt-dlp`, `ffmpeg`, `stirling-pdf` |

---

## Démarrage rapide

### Docker Compose (recommandé — inclut Stirling PDF)

Un **seul** `docker-compose.yml` couvre les deux modes, via la variable `TOOLBOX_IMAGE`.

**Mode build local (dev / CI)** :
```bash
git clone https://github.com/doalou/toolbox_everything.git
cd toolbox_everything
cp env.example .env          # puis édite SECRET_KEY
docker compose up -d --build
```

**Mode image Docker Hub (prod)** :
```bash
export TOOLBOX_IMAGE=doalo/toolbox-everything:1.3.0
docker compose pull
docker compose up -d
```

- Toolbox : http://localhost:8000
- Stirling PDF (embarqué via iframe) : http://localhost:8080

### Installation locale (sans Docker)

```bash
git clone https://github.com/doalou/toolbox_everything.git
cd toolbox_everything
python -m venv venv
source venv/bin/activate         # Linux/Mac
# venv\Scripts\activate          # Windows
pip install -r requirements.txt
python run.py --dev
```

Les outils PDF nécessitent Stirling PDF en parallèle (voir Configuration).

---

## Configuration

Copier `env.example` vers `.env` puis adapter :

| Variable | Description | Défaut |
|----------|-------------|--------|
| `SECRET_KEY` | Clé Flask — **à définir** en prod | auto-générée si absente |
| `APP_VERSION` | Version affichée dans le footer / healthcheck | `1.3.0` |
| `FLASK_ENV` | `development` ou `production` | `production` |
| `MAX_CONTENT_LENGTH` | Taille max des uploads (bytes) | `536870912` (512 MB) |
| `YOUTUBE_MAX_DURATION` | Durée max vidéo YouTube (secondes) | `3600` |
| `FFMPEG_PATH` | Chemin explicite vers FFmpeg | auto-détecté (`PATH`, `shutil.which`) |
| `STIRLING_PDF_URL` | URL **interne** de Stirling PDF (server-side healthcheck) | `http://stirling-pdf:8080` |
| `STIRLING_PDF_PUBLIC_URL` | URL **publique** utilisée par l'iframe (navigateur) | `http://localhost:8080` |
| `TOOLBOX_IMAGE` | Image Docker à utiliser (laisser vide = build local) | `toolbox-everything:1.3.0` |
| `TOOLBOX_PORT` / `STIRLING_PORT` | Ports hôte exposés | `8000` / `8080` |

---

## Structure du projet

```
toolbox_everything/
├── app/
│   ├── core/                     # Sécurité, exceptions métier
│   ├── services/
│   │   ├── main.py               # Factory Flask (logging, compress, healthcheck, errors)
│   │   ├── youtube_downloader/   # yt-dlp
│   │   ├── media_converter/      # FFmpeg / Pillow
│   │   ├── essentials/           # QR, password, hash, JSON, etc.
│   │   ├── pdf_tools/            # Iframe Stirling PDF + /pdf/status
│   │   └── common/               # Utilitaires partagés
│   ├── static/                   # CSS Tailwind + JS
│   └── templates/                # Jinja2
├── tests/                        # pytest (smoke + unit)
├── config.py                     # Configuration centralisée
├── run.py                        # CLI + cible Gunicorn (`run:app`)
├── Dockerfile                    # Image Toolbox (Python 3.11-slim)
├── docker-compose.yml            # Unifié (build local OU image hub via TOOLBOX_IMAGE)
├── requirements.txt              # Runtime
├── requirements-dev.txt          # Dev (pytest, black, flake8)
├── Makefile                      # setup, dev, test, test-cov, lint, docker-*
└── CHANGELOG.md
```

---

## Développement

```bash
make setup        # .env + SECRET_KEY + dépendances
make dev          # lance python run.py --dev sur :8000
make test         # pytest
make test-cov     # pytest + couverture
make lint         # flake8
make format       # black
make docker-build # construit l'image avec APP_VERSION
```

Bannière ASCII au démarrage, logs rotatifs dans `logs/toolbox.log` (5 MB × 5).

---

## Endpoints principaux

| Route | Description |
|-------|-------------|
| `GET /` | Accueil / dashboard |
| `GET /youtube/` | Téléchargeur YouTube |
| `GET /media/` | Convertisseur média |
| `GET /essentials/` | Outils essentiels |
| `GET /pdf/` | Outils PDF (iframe Stirling) |
| `GET /pdf/status` | Statut JSON de Stirling PDF |
| `GET /health` | Healthcheck JSON (version, yt-dlp, ffmpeg, stirling) |

---

## Licence

[MIT](LICENSE).
