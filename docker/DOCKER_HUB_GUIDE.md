# 🐳 Guide Docker Hub - Toolbox Everything

Ce guide vous explique comment publier et utiliser votre image Docker sur Docker Hub.

## 📋 Prérequis

1. **Compte Docker Hub** : [Créez un compte](https://hub.docker.com/)
2. **Docker installé** : Version 20.10+
3. **Git** : Pour cloner le projet

## 🚀 Publication sur Docker Hub

### Étape 1: Configuration

1. **Remplacez `doalou`** dans tous les fichiers par votre nom d'utilisateur Docker Hub :
   - `docker/docker-build.sh`
   - `docker/docker-build.ps1`
   - `docker/docker-compose.hub.yml`
   - `docker/README.docker-hub.md`
   - `docker/Makefile`

2. **Connectez-vous à Docker Hub** :
   ```bash
   docker login
   ```

### Étape 2: Build et Push

#### Option A: Script automatique (Recommandé)

**Sur Windows (PowerShell)** :
```powershell
cd docker
.\docker-build.ps1 "1.1.2" "votre-username"
```

**Sur Linux/Mac** :
```bash
cd docker
chmod +x docker-build.sh
./docker-build.sh "1.1.2" "votre-username"
```

#### Option B: Makefile
```bash
cd docker
make push USERNAME=votre-username VERSION=1.0.0
```

#### Option C: Commandes manuelles
```bash
# Build avec tous les tags (depuis la racine)
docker build -t votre-username/toolbox-everything:latest .
docker build -t votre-username/toolbox-everything:1.0.0 .
docker build -t votre-username/toolbox-everything:v1.0.0 .

# Push vers Docker Hub
docker push votre-username/toolbox-everything:latest
docker push votre-username/toolbox-everything:1.0.0
docker push votre-username/toolbox-everything:v1.0.0
```

## 🎯 Utilisation de l'image publiée

### Lancement simple
```bash
docker run -d -p 8000:8000 votre-username/toolbox-everything
```

### Avec Docker Compose
Utilisez le fichier `docker/docker-compose.hub.yml` :
```bash
# Modifiez d'abord l'image dans docker/docker-compose.hub.yml
# image: votre-username/toolbox-everything:latest

docker-compose -f docker/docker-compose.hub.yml up -d
```

### Avec persistance des données
```bash
docker run -d \
  --name toolbox \
  -p 8000:8000 \
  -v toolbox_uploads:/app/uploads \
  -v toolbox_downloads:/app/downloads \
  -v toolbox_logs:/app/logs \
  votre-username/toolbox-everything
```

## 📝 Page Docker Hub

Après publication, copiez le contenu de `docker/README.docker-hub.md` dans la description de votre repository Docker Hub pour une documentation complète.

## 🔄 Mise à jour de l'image

### 1. Modifier le code source
### 2. Mettre à jour la version

Dans `Dockerfile`, mettez à jour :
```dockerfile
LABEL version="1.1.0"
```

### 3. Republier
```bash
# Avec script
cd docker
.\docker-build.ps1 "1.1.0" "votre-username"

# Ou avec Makefile
cd docker
make push USERNAME=votre-username VERSION=1.1.0
```

## 📂 Structure du projet

```
toolbox_everything/
├── Dockerfile              # Dockerfile principal (racine)
├── .dockerignore           # Exclusions Docker (racine)  
├── docker-compose.yml      # Compose de développement (racine)
├── docker/                 # 📁 Dossier Docker Hub
│   ├── docker-build.sh     # Script de build Linux/Mac
│   ├── docker-build.ps1    # Script de build Windows
│   ├── docker-compose.hub.yml  # Compose pour Docker Hub
│   ├── Makefile            # Commandes automatisées
│   ├── README.docker-hub.md    # Documentation Docker Hub
│   └── DOCKER_HUB_GUIDE.md     # Ce guide
├── app/                    # Code source de l'application
├── requirements.txt        # Dépendances Python
└── ...
```

## 📊 Commandes utiles

### Vérifier l'état
```bash
# Statut du conteneur
docker ps

# Logs en temps réel
docker logs -f toolbox_everything

# Informations sur l'image
docker images votre-username/toolbox-everything
```

### Maintenance
```bash
# Nettoyer les anciennes images (depuis docker/)
cd docker
make clean USERNAME=votre-username

# Ou manuellement
docker system prune -a
```

## 🛠️ Résolution de problèmes

### Erreur de connexion Docker Hub
```bash
docker logout
docker login
```

### Image trop volumineuse
- Vérifiez le `.dockerignore` (à la racine)
- Utilisez le multi-stage build (déjà configuré)

### Erreurs de build
```bash
# Build sans cache (depuis la racine)
docker build --no-cache -t votre-username/toolbox-everything .
```

### Scripts ne fonctionnent pas
- Assurez-vous d'être dans le dossier `docker/` pour exécuter les scripts
- Vérifiez que le `Dockerfile` est bien à la racine du projet

## 📱 Tags recommandés

- `latest` : Version stable actuelle
- `1.0.0` : Version spécifique
- `v1.0.0` : Version avec préfixe v
- `dev` : Version de développement (optionnel)

## 🌟 Meilleures pratiques

1. **Versioning sémantique** : `MAJOR.MINOR.PATCH`
2. **Tags multiples** : `latest` + version spécifique
3. **Documentation complète** : README Docker Hub détaillé
4. **Tests automatisés** : Vérifiez que l'image fonctionne
5. **Sécurité** : Utilisateur non-root, image minimale
6. **Organisation** : Fichiers Docker dans `docker/`, `Dockerfile` à la racine

## 🎯 Automatisation CI/CD

### GitHub Actions (exemple)
```yaml
name: Docker Hub Publish
on:
  push:
    tags: [ 'v*' ]
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - name: Build and push
        run: |
          cd docker
          ./docker-build.sh ${GITHUB_REF#refs/tags/v} ${{ secrets.DOCKERHUB_USERNAME }}
```

## 📞 Support

- **Issues** : Utilisez GitHub Issues pour les problèmes
- **Documentation** : README.md principal du projet
- **Docker Hub** : Page de l'image pour les questions d'utilisation

---

**🎉 Félicitations ! Votre application est maintenant disponible sur Docker Hub !** 