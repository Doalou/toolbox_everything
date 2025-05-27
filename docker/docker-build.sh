#!/bin/bash

set -e

DEFAULT_VERSION="1.1.3"
DEFAULT_USERNAME="doalou"

VERSION=${1:-$DEFAULT_VERSION}
USERNAME=${2:-$DEFAULT_USERNAME}
IMAGE_NAME="toolbox-everything"
FULL_IMAGE="$USERNAME/$IMAGE_NAME"

echo "🚀 Building Docker image for Docker Hub"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 Image: $FULL_IMAGE"
echo "🏷️  Version: $VERSION"
echo "👤 Username: $USERNAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ! docker info > /dev/null 2>&1; then
    echo "❌ Erreur: Docker n'est pas en cours d'exécution"
    exit 1
fi

cd ..

echo "🔨 Building image..."
docker build \
    --tag "$FULL_IMAGE:latest" \
    --tag "$FULL_IMAGE:$VERSION" \
    --tag "$FULL_IMAGE:v$VERSION" \
    .

echo "✅ Build terminé avec succès!"

echo "📋 Images créées:"
docker images "$FULL_IMAGE"

read -p "🤔 Voulez-vous push les images vers Docker Hub? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Pushing images to Docker Hub..."
    
    echo "🔐 Vérification de la connexion Docker Hub..."
    if ! docker info | grep -q "Username"; then
        echo "🔑 Connexion à Docker Hub requise:"
        docker login
    fi
    
    echo "⬆️  Pushing $FULL_IMAGE:latest..."
    docker push "$FULL_IMAGE:latest"
    
    echo "⬆️  Pushing $FULL_IMAGE:$VERSION..."
    docker push "$FULL_IMAGE:$VERSION"
    
    echo "⬆️  Pushing $FULL_IMAGE:v$VERSION..."
    docker push "$FULL_IMAGE:v$VERSION"
    
    echo "🎉 Push terminé avec succès!"
    echo "🌐 Votre image est maintenant disponible sur:"
    echo "   https://hub.docker.com/r/$USERNAME/$IMAGE_NAME"
else
    echo "⏸️  Push annulé. Vous pouvez push manuellement avec:"
    echo "   docker push $FULL_IMAGE:latest"
    echo "   docker push $FULL_IMAGE:$VERSION"
fi

echo "✨ Terminé!" 