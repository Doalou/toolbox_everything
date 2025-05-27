# 🧰 Toolbox Everything

Une boîte à outils web complète avec téléchargeur YouTube, convertisseur de médias et outils utilitaires, le tout dans une interface moderne et responsive.

## ✨ Fonctionnalités

- **🎬 Téléchargeur YouTube** - Téléchargez des vidéos et audio depuis YouTube en différentes qualités
- **🔄 Convertisseur de médias** - Convertissez entre différents formats d'images et vidéos  
- **🔧 Outils essentiels** - Générateur de QR codes, raccourcisseur d'URL, et plus
- **📱 Interface responsive** - Fonctionne parfaitement sur desktop et mobile
- **🐳 Docker ready** - Conteneurisé et prêt pour Docker Hub

## 🚀 Installation et lancement

### Option 1: Docker (Recommandé)

#### Depuis Docker Hub
```bash
docker run -d -p 8000:8000 --name toolbox doalo/toolbox-everything
```

#### Build local
```bash
# Clone du projet
git clone https://github.com/doalou/toolbox_everything.git
cd toolbox_everything

# Build et lancement avec Docker Compose
docker-compose up -d
```

### Option 2: Installation Python

```bash
# Clone et installation
git clone https://github.com/doalou/toolbox_everything.git
cd toolbox_everything

# Installation des dépendances  
pip install -r requirements.txt

# Lancement
python run.py
```

Accédez ensuite à http://localhost:8000

## 🐳 Docker Hub

Ce projet est optimisé pour Docker Hub avec une organisation complète dans le dossier `docker/`.

### Publication rapide sur Docker Hub

**Windows :**
```powershell
cd docker
.\docker-build.ps1 "1.0.0" "votre-username"
```

**Linux/Mac :**
```bash
cd docker
chmod +x docker-build.sh
./docker-build.sh "1.0.0" "votre-username"
```

**Avec Make :**
```bash
cd docker
make push USERNAME=votre-username VERSION=1.0.0
```

📖 **Guide complet** : Consultez `docker/DOCKER_HUB_GUIDE.md` pour un guide détaillé.

## 📂 Structure du projet

```
toolbox_everything/
├── 📁 app/                    # Code source de l'application
│   ├── core/                  # Modules principaux (sécurité, exceptions)
│   ├── services/              # Services métier
│   │   ├── main.py           # Factory de l'application Flask
│   │   ├── youtube_downloader/ # Service téléchargement YouTube
│   │   ├── media_converter/   # Service conversion de médias
│   │   ├── essentials/        # Outils utilitaires
│   │   └── common/            # Utilitaires partagés
│   ├── static/               # Fichiers statiques (CSS, JS)
│   └── templates/            # Templates HTML
├── 📁 docker/                # 🐳 Outils Docker Hub
│   ├── docker-build.sh      # Script build Linux/Mac
│   ├── docker-build.ps1     # Script build Windows
│   ├── docker-compose.hub.yml # Compose pour Docker Hub
│   ├── Makefile             # Commandes automatisées
│   ├── README.md            # Documentation du dossier
│   ├── README.docker-hub.md # Doc pour page Docker Hub
│   └── DOCKER_HUB_GUIDE.md  # Guide complet Docker Hub
├── 🐳 Dockerfile            # Image Docker principale
├── 🐙 docker-compose.yml    # Compose de développement  
├── 📋 requirements.txt      # Dépendances Python
├── 🏃 run.py               # Point d'entrée de l'application
├── ⚙️  config.py            # Configuration
└── 📖 README.md            # Ce fichier
```

## 🔧 Configuration

### Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `FLASK_ENV` | Environnement Flask | `production` |
| `FLASK_APP` | Point d'entrée | `run.py` |
| `MAX_CONTENT_LENGTH` | Taille max des uploads | `512MB` |
| `YOUTUBE_MAX_DURATION` | Durée max vidéo YouTube | `3600s` |

### Dossiers de données

- `uploads/` - Fichiers uploadés temporaires
- `downloads/` - Fichiers téléchargés (YouTube, etc.)  
- `logs/` - Fichiers de logs de l'application

## 🛠️ Développement

### Prérequis

- Python 3.11+
- Docker (optionnel)
- FFmpeg (pour la conversion de médias)

### Installation locale

```bash
# Clone du repo
git clone https://github.com/doalou/toolbox_everything.git
cd toolbox_everything

# Environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installation des dépendances
pip install -r requirements.txt

# Lancement en mode développement
python run.py
```

### Tests Docker

```bash
# Build et test local
docker-compose up --build

# Ou avec les outils Docker Hub
cd docker
make test USERNAME=votre-username
```

## 📱 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` | Interface principale |
| `/youtube` | Téléchargeur YouTube |
| `/media` | Convertisseur de médias |
| `/essentials` | Outils utilitaires |

## 🤝 Contribution

1. Fork du projet
2. Créez votre branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit vos changements (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence [MIT](LICENSE).

## 🆘 Support

- **Issues** : [GitHub Issues](https://github.com/doalou/toolbox_everything/issues)

---

**⭐ Si ce projet vous est utile, n'hésitez pas à lui donner une étoile !**
