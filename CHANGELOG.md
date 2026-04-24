# Changelog

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Versionnage Sémantique](https://semver.org/lang/fr/).

---

## [1.3.0] - 2026-04-24

### Ajouté
- **Logo & branding** : deux variantes SVG (`app/static/img/logo.svg` transparent + `logo-filled.svg` avec fond) — utilisées en header, favicon (y.c. `apple-touch-icon` et `mask-icon`), hero de la page d'accueil (avec animation flottante + `prefers-reduced-motion`) et Open Graph / Twitter cards
- **Outils PDF (Stirling PDF) — mode amnésique** : nouveau blueprint `/pdf` qui embarque [Stirling PDF](https://github.com/Stirling-Tools/Stirling-PDF) via iframe, configuré pour une instance **publique sans rétention de données** :
  - `/configs`, `/logs` et `/tmp` montés en **`tmpfs`** (RAM uniquement, effacés à chaque restart du container)
  - Toutes les analytics désactivées : `SYSTEM_ENABLEANALYTICS=false`, `SYSTEM_ENABLEPOSTHOG=false`, `SYSTEM_ENABLESCARF=false`, `SYSTEM_GOOGLEVISIBILITY=false`, `SHOW_SURVEY=false`, `METRICS_ENABLED=false`, `SYSTEM_SHOWUPDATE=false`
  - Fichiers temp nettoyés agressivement : `MAXAGEHOURS=1`, `CLEANUPINTERVALMINUTES=5`, `STARTUPCLEANUP=true`, `CLEANUPSYSTEMTEMP=true`
  - Features à risque SSRF/privacy désactivées : `SYSTEM_ENABLEURLTOPDF=false`, `SYSTEM_ENABLEMOBILESCANNER=false`, `STORAGE_ENABLED=false`, audit enterprise explicitement off
  - `security_opt: no-new-privileges:true`
  - Seul volume persistant : `stirling_tessdata` (modèles OCR Tesseract, données statiques non-utilisateur)
- **Docker Compose** : service `stirling-pdf` (image `stirlingtools/stirling-pdf:latest`) avec limites de ressources et dépendance ordonnée depuis `toolbox`
- **Variables d'env** : `STIRLING_PDF_URL` (URL interne Docker) et `STIRLING_PDF_PUBLIC_URL` (URL navigateur pour iframe)
- **Healthcheck** : endpoint `/health` exposant le statut de `yt_dlp`, `ffmpeg` et `stirling_pdf` (utilisé par le healthcheck Docker)
- **Tests** : suite pytest avec fixtures partagées (`tests/conftest.py`), 27 tests smoke + unitaires (routes, config, outils essentiels, PDF fallback)
- **requirements-dev.txt** : dépendances développement (pytest, pytest-cov, black, flake8, isort)
- **Makefile** : cible `test-cov` pour lancer les tests avec rapport de couverture

### Modifié
- **Factory Flask** (`app/services/main.py`) : logging unifié via `RotatingFileHandler` (5MB × 5 fichiers), `Flask-Compress` initialisé une seule fois dans `create_app`, bannière ASCII imprimée une seule fois (gate via `TOOLBOX_PRINT_BANNER`), `ProxyFix` avec paramètres explicites, `SEND_FILE_MAX_AGE_DEFAULT` pour le cache des statiques
- **Middleware requêtes** : remplacement de `validate_request` par `_request_start`/`_request_end` avec `time.perf_counter()` — filtrage `/static` et `/health` pour éviter le bruit dans les logs
- **Gestion erreurs** : handler HTTPException centralisé dans `main.py` (HTML pour UI, JSON pour API détecté via `X-Requested-With` ou path `/api/`), `exceptions.py` réservé aux exceptions métier `ToolboxBaseException`
- **FFmpeg** : détection unifiée via `Config.get_ffmpeg_path()` (env var `FFMPEG_PATH`, `shutil.which`, chemins Linux/Windows) — suppression du `.exe` hardcodé multi-plateformes
- **YouTube Downloader** : `tempfile.mkdtemp()` + `@after_this_request` pour garantir le nettoyage des fichiers temporaires, User-Agent Chrome plus récent, classification unifiée des erreurs via `_classify_yt_error`
- **Media Converter** : paramètre `quality` (0-100) désormais effectif sur les vidéos — mapping vers CRF FFmpeg (libx264 / libvpx-vp9) via `_quality_to_crf`
- **URL Validator** : listes de domaines autorisés centralisées dans `config.py` comme source unique (récupérées via `current_app.config`)
- **Homepage** : carte « Outils PDF » (violet) avec CTA dynamique (« Ouvrir » ou « Configurer » selon l'état Stirling)
- **Navigation** : lien PDF actif dans header desktop + mobile avec badge « setup » si Stirling non configuré
- **Page PDF** : ton épuré — suppression des copies marketing (« 150+ outils », « sans envoyer vos documents à un tiers », sous-titres explicatifs redondants), toolbar réduite au titre **« Instance Stirling PDF »** + un simple dot d'état (vert/jaune), bouton « Ouvrir dans un nouvel onglet » en icône seule, bloc fallback avec un seul `docker compose up -d`. Section **« Pourquoi utiliser nos outils ? »** incluse en bas comme sur les autres pages (via `tool_features.html`)
- **Footer** : réduit à l'essentiel — une seule ligne `© {year} · v{version}` + icône GitHub, suppression des liens dupliqués (YouTube/Conversion/Essentiels/PDF déjà dans le header) et du tagline « open source, self-hosted »

### Supprimé
- **`docker-compose.yml` / `docker-compose.hub.yml`** : fusionnés en un unique **`compose.yml`** à la racine (nom moderne recommandé par Compose v2) — toggle build local vs image Docker Hub via `TOOLBOX_IMAGE`, ports configurables via `TOOLBOX_PORT` / `STIRLING_PORT`
- **Dossier `docker/`** : scripts et docker-compose migrés à la racine
  - `docker/Makefile`, `docker/docker-build.ps1`, `docker/docker-build.sh` supprimés
  - `docker/docker-compose.hub.yml` déplacé à la racine puis fusionné
- **Dossier `bin/`** : plus nécessaire — FFmpeg détecté dynamiquement via `PATH` ou image Docker
- **CSS morte** : classes inutilisées retirées de `app/static/css/style.css` (`.card-hover-effect`, `.animated-gradient-text`, `.floating-icon`, `.pulse-on-hover`, `.glow-effect`, `.skeleton` et leurs `@keyframes`)
- **Handlers 404/500 dupliqués** : consolidés dans `main.py`, retirés de `exceptions.py`

### Corrigé
- **Bannière ASCII imprimée N fois sous Gunicorn** : n'apparaît désormais qu'une seule fois au démarrage
- **`Flask-Compress` sans effet sous Gunicorn** : initialisé correctement dans `create_app`
- **Chemin FFmpeg Windows hardcodé** sur builds Linux : logique désormais cross-platform
- **Validation de requête trop stricte** : ne bloque plus les requêtes légitimes sans User-Agent
- **Quality vidéo ignorée** dans le media converter : désormais appliquée via CRF

---

## [1.2.0] - 2026-04-10

### Ajouté
- **Design system** : nouveau système CSS partagé pour les pages outils (`.tool-panel`, `.tool-btn`, `.tool-input`, `.tool-select`, `.tool-progress`, `.tool-dropzone`, `.tool-hero`)
- **Footer** : année de copyright dynamique et numéro de version (`v{{ app_version }}`) via context processor
- **Démarrage** : bannière ASCII au lancement avec version, mode, URL, Python, FFmpeg, uploads et routes
- **CLI** : `python run.py --version` utilise désormais `__version__` au lieu d'une valeur hardcodée
- **Sécurité** : auto-génération de `SECRET_KEY` à la première configuration (`make setup`, Docker build, ou au démarrage si le placeholder est détecté)
- **YouTube Downloader** : téléchargement parallèle des fragments HLS/DASH (`concurrent_fragment_downloads: 4`)
- **YouTube Downloader** : retries automatiques (3 tentatives sur les requêtes et fragments)
- **YouTube Downloader** : User-Agent Chrome pour éviter les blocages anti-bot
- **YouTube Downloader** : gestion des erreurs YouTube Premium et vidéos nécessitant une connexion
- **YouTube Downloader** : fallback `channel` → `uploader` pour l'affichage du nom de chaîne

### Modifié
- **Header** : refonte complète en flat design — barre unique, navigation centrée en pill, branding allégé avec accent coloré
- **Header** : dropdown « Essentiels » centré sous le bouton avec pont invisible pour le hover
- **Header** : menu mobile simplifié en panneau léger avec sous-menu dépliable
- **Homepage** : refonte visuelle avec hero compact, grille 4 colonnes, CTA colorés et section « Pourquoi »
- **Page Essentiels** : refonte en grille de cartes horizontales cliquables avec icônes colorées et flèche au hover
- **Page YouTube** : refonte avec `.tool-panel`, `.tool-btn`, `.tool-input` — suppression des ombres lourdes et effets scale
- **Page Conversion Média** : refonte avec `.tool-dropzone`, `.tool-panel`, `.tool-select` — zone de dépôt flat, overlay allégé
- **Textes** : correction de tous les accents manquants sur l'ensemble des templates
- **YouTube Downloader** : mise à jour de `yt-dlp` de `2025.06.25` vers `2026.03.17`
- **YouTube Downloader** : format de sélection vidéo migré vers `bestvideo+bestaudio` (streams séparés mergés par FFmpeg)
- **YouTube Downloader** : passage à un seul appel `extract_info(download=True)` avec `requested_downloads[0]['filepath']`
- **YouTube Downloader** : factorisation des options communes dans `_common_ydl_opts()`
- **Dépendances** : mise à jour globale de toutes les dépendances :
  - Flask `3.0.2` → `3.1.3`
  - Werkzeug `3.0.6` → `3.1.8`
  - python-dotenv `1.0.1` → `1.2.2`
  - Flask-WTF `1.2.1` → `1.2.2`
  - Flask-Compress `1.14` → `1.24`
  - Flask-Caching `2.1.0` → `2.3.1`
  - Pillow `10.3.0` → `12.2.0`
  - qrcode `7.4.2` → `8.2`
  - shortuuid `1.0.11` → `1.0.13`
  - cryptography `42.0.2` → `46.0.7`
  - requests `2.32.2` → `2.33.1`
  - python-dateutil `2.8.2` → `2.9.0.post0`
  - humanize `4.9.0` → `4.15.0`
  - gunicorn `23.0.0` → `25.3.0`
  - brotli `1.1.0` → `1.2.0`
  - orjson `3.9.15` → `3.11.8`
  - certifi `≥2024.2.2` → `≥2026.2.25`
  - urllib3 `≥2.2.0` → `≥2.6.3`
  - bleach `6.1.0` → `6.3.0`
  - psutil `5.9.8` → `7.2.2`
  - marshmallow `3.21.1` → `4.3.0`
  - validators `0.22.0` → `0.35.0`

### Corrigé
- **YouTube Downloader** : suppression de l'appel à `ydl._format_selection()` (méthode privée supprimée en 2026.x)
- **YouTube Downloader** : suppression des options `prefer_ffmpeg` et `keepvideo` dépréciées/supprimées dans yt-dlp 2026.x
- **Frontend** : `textContent` assigné au `<span>` enfant plutôt qu'au `<p>` parent pour ne plus écraser les icônes FontAwesome dans les métadonnées vidéo

---

## [1.1.3] - 2024

### Modifié
- Mise à jour mineure de l'application
- `gunicorn` mis à jour de `21.2.0` vers `23.0.0` (sécurité)
- `werkzeug` mis à jour de `3.0.1` vers `3.0.6` (sécurité)
- `pillow` mis à jour de `10.2.0` vers `10.3.0` (sécurité)
- `requests` mis à jour de `2.31.0` vers `2.32.2` (sécurité)

---

## [1.1.2c] - 2024

### Corrigé
- Corrections diverses

---

## [1.1.2b] - 2024

### Corrigé
- Correctifs supplémentaires de la 1.1.2

---

## [1.1.2] - 2024

### Modifié
- Améliorations générales de stabilité

---

## [1.1.1] - 2024

### Corrigé
- Correctifs de la version 1.1

---

## [1.1.0] - 2024

### Ajouté
- Préparation et mise en production de la version 1.1
- Séparation du JavaScript et du HTML dans les templates
- Amélioration du padding et de l'interface

---

## [1.0.0] - 2024

### Ajouté
- Création initiale du projet
- **YouTube Downloader** : téléchargement de vidéos et audio depuis YouTube
- **Convertisseur de médias** : conversion entre formats d'images et vidéos
- **Outils essentiels** : générateur de QR codes, générateur de mots de passe, raccourcisseur d'URL
- Interface responsive desktop et mobile
- Support Docker et Docker Compose
- Pipeline CI/CD GitHub Actions (build & publish Docker Hub)