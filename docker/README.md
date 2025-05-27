# 🐳 Dossier Docker - Toolbox Everything

Ce dossier contient tous les outils et fichiers nécessaires pour la gestion Docker Hub de **Toolbox Everything**.

## 📂 Structure

```
docker/
├── docker-build.sh           # 🐧 Script de build/push Linux/Mac
├── docker-build.ps1          # 🪟 Script de build/push Windows  
├── docker-compose.hub.yml    # 🐙 Compose pour image Docker Hub
├── Makefile                  # ⚙️  Commandes automatisées
├── README.docker-hub.md      # 📖 Documentation pour Docker Hub
├── DOCKER_HUB_GUIDE.md       # 📚 Guide complet Docker Hub
└── README.md                 # 📄 Ce fichier
```

## 🚀 Utilisation rapide

### 1. Publication sur Docker Hub

**Windows :**
```powershell
cd docker
.\docker-build.ps1 "1.1.2" "doalou"
```

**Linux/Mac :**
```bash
cd docker
chmod +x docker-build.sh
./docker-build.sh "1.1.2" "doalou"
```

**Avec Make :**
```bash
cd docker
make push USERNAME=doalou VERSION=1.1.2
```

### 2. Utilisation depuis Docker Hub

**Lancement direct :**
```bash
docker run -d -p 8000:8000 doalou/toolbox-everything
```

**Avec Docker Compose :**
```bash
# Modifiez d'abord docker-compose.hub.yml avec votre username
docker-compose -f docker/docker-compose.hub.yml up -d
```

## 📋 Fichiers expliqués

### 🔨 Scripts de build

- **`docker-build.sh`** : Script Bash pour Linux/Mac
- **`docker-build.ps1`** : Script PowerShell pour Windows
- **`Makefile`** : Commandes make multi-plateformes

Ces scripts :
- Buildent l'image avec plusieurs tags (`latest`, `version`, `v-version`)
- Pushent automatiquement vers Docker Hub
- Gèrent la connexion Docker Hub
- Naviguent vers le répertoire parent pour le contexte de build

### 🐙 Docker Compose

- **`docker-compose.hub.yml`** : Configuration pour utiliser l'image depuis Docker Hub au lieu de la builder localement

### 📖 Documentation

- **`README.docker-hub.md`** : Documentation à copier sur la page Docker Hub
- **`DOCKER_HUB_GUIDE.md`** : Guide complet pour publier et utiliser l'image
- **`README.md`** : Ce fichier d'aide

## ⚙️ Commandes Make disponibles

```bash
make help              # Affiche l'aide
make build             # Build simple  
make hub-build         # Build avec tous les tags
make push              # Build + push vers Docker Hub
make hub-push          # Push uniquement (si déjà build)
make run               # Lance le conteneur
make stop              # Arrête le conteneur
make logs              # Affiche les logs
make test              # Teste l'image
make clean             # Nettoie tout
make info              # Infos sur l'image
```

## 🔧 Configuration

### Variables par défaut

Tous les scripts utilisent ces valeurs par défaut :
- **USERNAME** : `doalou` 
- **VERSION** : `1.1.2`
- **IMAGE_NAME** : `toolbox-everything`

### Personnalisation

**Scripts :**
```bash
./docker-build.sh "1.1.2" "doalou"
```

**Make :**
```bash
make push USERNAME=doalou VERSION=1.1.2
```

## 📝 Avant publication

1. **Connectez-vous à Docker Hub :**
   ```bash
   docker login
   ```

2. **Testez localement :**
   ```bash
   cd docker
   make test USERNAME=doalou
   ```

## ⚠️ Points importants

- **Exécution** : Tous les scripts doivent être exécutés depuis le dossier `docker/`
- **Contexte** : Le build utilise le répertoire parent `..` comme contexte
- **Dockerfile** : Reste à la racine du projet pour accéder à tous les fichiers
- **Tags** : Création automatique de `latest`, `version` et `v-version`

## 🆘 Dépannage

### Script ne fonctionne pas
```bash
# Vérifiez que vous êtes dans le bon dossier
pwd  # Doit afficher .../toolbox_everything/docker
```

### Erreur de build
```bash
# Vérifiez que Dockerfile existe dans le parent
ls ../Dockerfile
```

### Permission denied (Linux/Mac)
```bash
chmod +x docker-build.sh
```

## 🔗 Liens utiles

- **Docker Hub** : [hub.docker.com](https://hub.docker.com/)
- **Documentation complète** : `DOCKER_HUB_GUIDE.md`
- **Image finale** : `https://hub.docker.com/r/doalou/toolbox-everything`

---

**💡 Conseil** : Consultez `DOCKER_HUB_GUIDE.md` pour un guide détaillé pas à pas ! 