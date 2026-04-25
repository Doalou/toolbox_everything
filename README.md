# Toolbox Everything

> Une boîte à outils web, modulaire et sans prise de tête : télécharger une vidéo (YouTube, Vimeo, Dailymotion, TikTok), convertir un média, bidouiller un QR code ou un hash, et manipuler des PDF sans quitter son navigateur.

Stack : **Flask + Tailwind**, tout en Docker, prêt à être posé derrière un reverse proxy.

![version](https://img.shields.io/badge/version-1.3.1-blue)
![python](https://img.shields.io/badge/python-3.12-3776AB?logo=python&logoColor=white)
![flask](https://img.shields.io/badge/flask-3.1-000000?logo=flask)
![license](https://img.shields.io/badge/license-MIT-green)

---

## Ce qu'il y a dedans

| Module | En deux mots |
|---|---|
| **Downloader vidéo / audio** | `yt-dlp` 2026.x, multi-plateformes (YouTube, Vimeo, Dailymotion, TikTok), fragments en parallèle, merge `bestvideo+bestaudio` via FFmpeg. |
| **Convertisseur Média** | Images (PNG, JPG, WebP, GIF, etc.) et vidéos (MP4, WebM, MKV, etc.) avec contrôle qualité mappé sur le CRF de FFmpeg. |
| **Outils Essentiels** | 13 outils 100% client-side : QR codes, mots de passe (+ passphrase), SHA-1/256/384/512, Base64, JSON formatter, palettes, timestamps, UUID v4/v7, JWT decoder, regex tester, URL encoder, Lorem Ipsum, diff. Rien n'est envoyé au serveur. |
| **Outils PDF** | 150+ opérations via **Stirling PDF** embarqué (fusion, split, OCR, compression, signature, watermark). Instance **amnésique** : `/configs`, `/logs` et `/tmp` en RAM, zéro analytics, nettoyage temp toutes les 5 min. |
| **Healthcheck** | Un seul `/health` pour savoir si `yt-dlp`, `ffmpeg` et `stirling-pdf` répondent. |

---

## Démarrage rapide

### Avec Docker Compose (recommandé)

Un **unique** `compose.yml` couvre les deux modes de déploiement, choix via `TOOLBOX_IMAGE` :

```bash
git clone https://github.com/doalou/toolbox_everything.git
cd toolbox_everything
cp env.example .env          # édite au moins SECRET_KEY
docker compose up -d --build # build local (dev / CI)
```

Ou en prod avec l'image publique GHCR :

```bash
export TOOLBOX_IMAGE=ghcr.io/doalou/toolbox_everything:1.3.1
docker compose pull && docker compose up -d
```

Une fois démarré :

- Toolbox → <http://localhost:8000>
- Stirling PDF (iframe) → <http://localhost:8080>
- LibreSpeed (iframe) → <http://localhost:8081>

### En local (sans Docker)

```bash
python -m venv venv
# Linux / macOS
source venv/bin/activate
# Windows
# venv\Scripts\activate

pip install -r requirements.txt
make tailwind-build          # build CSS (télécharge le binaire au premier run)
python run.py --dev
```

> Les outils PDF et Speedtest nécessitent leurs services côté serveur. Voir la section Configuration ou lance `docker compose up -d`.
> Le rate limiter tombe sur `memory://` si aucun Redis n'est accessible. OK en dev.

---

## Configuration

Tout se passe dans `.env` (copié depuis `env.example`) :

| Variable | Rôle | Défaut |
|---|---|---|
| `SECRET_KEY` | Clé Flask, **à fixer** en prod | auto-générée si absente |
| `APP_VERSION` | Version affichée dans le footer / `/health` | `1.3.1` |
| `FLASK_ENV` | `development` ou `production` | `production` |
| `MAX_CONTENT_LENGTH` | Taille max des uploads (octets) | `536870912` (512 MB) |
| `FFMPEG_PATH` | Chemin explicite vers FFmpeg | auto-détecté (`shutil.which`) |
| `STIRLING_PDF_URL` | URL **interne** de Stirling PDF (healthcheck serveur) | `http://stirling-pdf:8080` |
| `STIRLING_PDF_PUBLIC_URL` | URL **publique** utilisée par l'iframe (navigateur) | `http://localhost:8080` |
| `LIBRESPEED_URL` | URL **interne** de LibreSpeed (healthcheck serveur) | `http://librespeed` |
| `LIBRESPEED_PUBLIC_URL` | URL **publique** utilisée par l'iframe (navigateur) | `http://localhost:8081` |
| `RATELIMIT_STORAGE_URI` | Backend du rate limiter (Redis en prod) | `redis://redis:6379/0` |
| `TOOLBOX_IMAGE` | Image Docker à tirer depuis GHCR | `ghcr.io/doalou/toolbox_everything:1.3.1` |
| `TOOLBOX_PORT` / `STIRLING_PORT` / `LIBRESPEED_PORT` | Ports hôte exposés | `8000` / `8080` / `8081` |

---

## Versioning et images GHCR

La version de référence est `VERSION`. Pour la v1.3.1, elle alimente :

- `APP_VERSION` dans l'application, le footer et `/health`.
- `docker build --build-arg APP_VERSION=...`.
- Le workflow GitHub Actions qui publie l'image sur GHCR.

Images publiées :

```bash
ghcr.io/doalou/toolbox_everything:1.3.1
ghcr.io/doalou/toolbox_everything:1.3
ghcr.io/doalou/toolbox_everything:latest
```

Règle de release :

1. Mettre à jour `VERSION`.
2. Reporter la version dans `env.example`, `compose.yml`, `Dockerfile`, le badge README et `CHANGELOG.md`.
3. Créer un tag Git `vX.Y.Z`.
4. Pousser le tag. Le workflow refuse un tag `vX.Y.Z` qui ne correspond pas au contenu de `VERSION`.
5. GitHub Actions publie et signe l'image `ghcr.io/doalou/toolbox_everything`.

Exemple :

```bash
git tag v1.3.1
git push origin v1.3.1
```

---

## Sécurité

La v1.3.1 durcit sérieusement la couche exposée (voir `CHANGELOG.md` pour le détail) :

- **CSP stricte avec nonce par requête**, `frame-ancestors 'none'`, `object-src 'none'`,
  Permissions-Policy verrouillée, HSTS conditionnel sur HTTPS.
- **Rate limiter Redis** (Flask-Limiter) sur les routes coûteuses : 3/min sur
  `/downloader/download`, 10/min sur `/media/convert`, etc.
- **Validation des uploads par magic bytes** (stdlib only, pas de `libmagic`),
  plafond batch 20 fichiers / 200 MB, garde anti-bombe Pillow (50 Mpx).
- **Whitelist yt-dlp** : YouTube, Vimeo, Dailymotion, TikTok uniquement.
  Les schemes `file://`, `ftp://`, `javascript:` sont explicitement bloqués.
- **Zéro CDN pour les assets critiques** : Tailwind est compilé localement
  (CLI standalone, sortie ~15 KB minifiée), Font Awesome rapatrié en
  `app/static/vendor/`, seul `qrcode-generator` reste en CDN avec SRI SHA-384
  obligatoire (enforcé par le modèle `ExternalScript`).

37 tests dédiés dans `tests/test_security.py`.

---

## Structure du projet

```
toolbox_everything/
├── app/
│   ├── core/                     # exceptions, rate_limit, security_headers, uploads
│   ├── services/
│   │   ├── main.py               # Factory Flask (logging, compress, /health, errors)
│   │   ├── downloader/           # yt-dlp (multi-plateformes)
│   │   ├── media_converter/      # FFmpeg / Pillow
│   │   ├── essentials/           # 13 outils client-side (registry auto-enregistrée)
│   │   ├── pdf_tools/            # Iframe Stirling PDF + /pdf/status
│   │   ├── speedtest/            # Iframe LibreSpeed + /speedtest/status
│   │   └── common/               # Utilitaires partagés
│   ├── static/
│   │   ├── css/input.css         # Source Tailwind → build vers tailwind.css
│   │   ├── vendor/fontawesome/   # Font Awesome 6.0.0 local (plus de CDN)
│   │   └── js/                   # JS applicatif + /essentials/*.js
│   └── templates/                # Jinja2
├── tests/                        # pytest (78 tests dont 37 sécurité)
├── config.py                     # Configuration centralisée
├── tailwind.config.js            # Config Tailwind (purge, couleurs, animations)
├── run.py                        # CLI + cible Gunicorn (`run:app`)
├── Dockerfile                    # Multi-stage : py-builder + css-builder + runtime
├── compose.yml                   # Toolbox + Stirling PDF + LibreSpeed + Redis
├── requirements.txt              # Runtime (audité, 0 dépendance morte)
├── requirements-dev.txt          # Dev (pytest, black, flake8)
├── Makefile                      # setup, dev, test, tailwind-*, docker-*
└── CHANGELOG.md
```

---

## Développement

```bash
make setup             # .env + SECRET_KEY + dépendances
make tailwind-install  # télécharge le binaire Tailwind CLI (une fois)
make tailwind-build    # build CSS minifié
make tailwind-watch    # build en continu (pour le dev CSS)
make dev               # python run.py --dev sur :8000
make test              # pytest (78 tests)
make test-cov          # pytest + couverture
make lint              # flake8
make format            # black
make docker-build      # construit les tags locaux et GHCR avec APP_VERSION
```

Bannière ASCII au boot (dev uniquement), logs rotatifs dans `logs/toolbox.log` (5 MB × 5).

---

## Endpoints principaux

| Route | Rôle |
|---|---|
| `GET /` | Accueil / dashboard |
| `GET /downloader/` | Téléchargeur vidéo / audio (YouTube, Vimeo, Dailymotion, TikTok) |
| `GET /downloader/info?url=...` | Métadonnées vidéo (JSON, 20/min) |
| `POST /downloader/download` | Téléchargement (JSON in, fichier out, 3/min) |
| `GET /media/` | Convertisseur média |
| `GET /essentials/` | Outils essentiels |
| `GET /pdf/` | Outils PDF (iframe Stirling) |
| `GET /pdf/status` | Statut JSON de Stirling PDF |
| `GET /speedtest/` | Speedtest (iframe LibreSpeed) |
| `GET /speedtest/status` | Statut JSON de LibreSpeed |
| `GET /health` | Healthcheck JSON (version, yt-dlp, ffmpeg, stirling, librespeed) |
| `GET /youtube/*` | Redirection 301/308 → `/downloader/*` (compat ascendante) |

---

## Licence

[MIT](LICENSE).
