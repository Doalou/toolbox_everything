# 🧰 Toolbox Everything - Docker Image

Une boîte à outils web complète avec téléchargeur YouTube et convertisseur de médias, empaquetée dans une image Docker prête à l'emploi.

## 🚀 Utilisation Rapide

```bash
docker run -d -p 8000:8000 --name toolbox yourusername/toolbox-everything

docker run -d -p 8000:8000 \
  -v toolbox_uploads:/app/uploads \
  -v toolbox_downloads:/app/downloads \
  -v toolbox_logs:/app/logs \
  --name toolbox \
  yourusername/toolbox-everything
```

Accédez ensuite à http://localhost:8000

## 📋 Fonctionnalités

- **🎬 Téléchargeur YouTube** - Téléchargez des vidéos et audio depuis YouTube
- **🔄 Convertisseur de médias** - Convertissez entre différents formats de médias
- **🔧 Outils essentiels** - QR codes, raccourcisseurs d'URL, et plus
- **📱 Interface responsive** - Fonctionne sur desktop et mobile

## 🐳 Docker Compose

Créez un fichier `docker-compose.yml` :

```yaml
services:
  toolbox:
    image: doalou/toolbox-everything:latest
    container_name: toolbox_everything
    ports:
      - "8000:8000"
    volumes:
      - toolbox_uploads:/app/uploads
      - toolbox_downloads:/app/downloads
      - toolbox_logs:/app/logs
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  toolbox_uploads:
  toolbox_downloads:
  toolbox_logs:
```

Puis lancez avec :
```bash
docker-compose up -d
```

## 🏷️ Tags Disponibles

- `latest` - Dernière version stable
- `1.0.0` - Version spécifique
- `v1.0.0` - Version avec préfixe v

## 🔧 Configuration

### Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|---------|
| `FLASK_ENV` | Environnement Flask | `production` |
| `FLASK_APP` | Point d'entrée Flask | `run.py` |
| `PYTHONUNBUFFERED` | Sortie Python non bufferisée | `1` |

### Volumes

| Volume | Description |
|--------|-------------|
| `/app/uploads` | Fichiers uploadés temporaires |
| `/app/downloads` | Fichiers téléchargés |
| `/app/logs` | Fichiers de logs |

### Ports

| Port | Description |
|------|-------------|
| `8000` | Interface web Gunicorn |

## 🛠️ Prérequis

- Docker 20.10+
- 512MB RAM minimum (1GB recommandé)
- 2GB d'espace disque libre

## 🔐 Sécurité

- L'image utilise un utilisateur non-root (`toolbox`)
- Multi-stage build pour une image optimisée
- Dépendances mises à jour et auditées

## 📊 Monitoring

L'image inclut un healthcheck intégré accessible via :
```bash
docker ps
docker logs toolbox_everything
```

## 🐛 Résolution de problèmes

### L'application ne démarre pas
```bash
docker logs toolbox_everything
docker ps -a
```

### Problèmes de permissions
```bash
docker-compose down -v
docker-compose up -d
```

### FFmpeg non disponible
FFmpeg est inclus dans l'image, mais certaines fonctionnalités avancées peuvent nécessiter des codecs spécifiques.

## 📱 Endpoints API

- `/` - Interface principale
- `/youtube` - Téléchargeur YouTube
- `/media` - Convertisseur de médias  
- `/essentials` - Outils utilitaires

## 🤝 Support

- **GitHub** : [lien-vers-votre-repo]
- **Issues** : [lien-vers-issues]
- **Wiki** : [lien-vers-wiki]

## 📄 Licence

Cette image Docker est distribuée sous licence [MIT](LICENSE).

---

**⭐ Si cette image vous est utile, n'hésitez pas à lui donner une étoile !** 