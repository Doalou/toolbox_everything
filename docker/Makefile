.PHONY: help build push clean test run stop logs hub-build hub-push

USERNAME ?= doalo
VERSION ?= 1.1.3
IMAGE_NAME = toolbox-everything
FULL_IMAGE = $(USERNAME)/$(IMAGE_NAME)
CONTAINER_NAME = toolbox-everything
BUILD_CONTEXT = ..

help:
	@echo "🧰 Toolbox Everything - Docker Hub Commands"
	@echo "════════════════════════════════════════════"
	@echo ""
	@echo "📦 Build & Push:"
	@echo "  make build         - Build l'image localement"
	@echo "  make push          - Push vers Docker Hub"
	@echo "  make hub-build     - Build avec tous les tags pour Docker Hub"
	@echo "  make hub-push      - Push tous les tags vers Docker Hub"
	@echo ""
	@echo "🚀 Run & Test:"
	@echo "  make run           - Lance le conteneur"
	@echo "  make stop          - Arrête le conteneur"
	@echo "  make logs          - Affiche les logs"
	@echo "  make test          - Teste l'image"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  make clean         - Nettoie les images/conteneurs"
	@echo ""
	@echo "⚙️  Variables:"
	@echo "  USERNAME=$(USERNAME)"
	@echo "  VERSION=$(VERSION)"
	@echo "  IMAGE_NAME=$(IMAGE_NAME)"
	@echo ""
	@echo "💡 Exemples:"
	@echo "  make hub-build USERNAME=monusername VERSION=1.1.0"
	@echo "  make run USERNAME=monusername"
	@echo ""
	@echo "📂 Context: $(BUILD_CONTEXT) (répertoire parent)"

build:
	@echo "🔨 Building $(FULL_IMAGE):$(VERSION)..."
	docker build -t $(FULL_IMAGE):$(VERSION) $(BUILD_CONTEXT)

hub-build:
	@echo "🚀 Building $(FULL_IMAGE) for Docker Hub..."
	docker build \
		-t $(FULL_IMAGE):latest \
		-t $(FULL_IMAGE):$(VERSION) \
		-t $(FULL_IMAGE):v$(VERSION) \
		$(BUILD_CONTEXT)
	@echo "✅ Build terminé!"
	@docker images $(FULL_IMAGE)

push: hub-build
	@echo "📤 Pushing to Docker Hub..."
	docker push $(FULL_IMAGE):latest
	docker push $(FULL_IMAGE):$(VERSION)
	docker push $(FULL_IMAGE):v$(VERSION)
	@echo "🎉 Push terminé!"

hub-push:
	@echo "📤 Pushing existing images to Docker Hub..."
	docker push $(FULL_IMAGE):latest
	docker push $(FULL_IMAGE):$(VERSION)
	docker push $(FULL_IMAGE):v$(VERSION)

run:
	@echo "🚀 Running $(CONTAINER_NAME)..."
	@docker stop $(CONTAINER_NAME) 2>/dev/null || true
	@docker rm $(CONTAINER_NAME) 2>/dev/null || true
	docker run -d \
		--name $(CONTAINER_NAME) \
		-p 8000:8000 \
		-v toolbox_uploads:/app/uploads \
		-v toolbox_downloads:/app/downloads \
		-v toolbox_logs:/app/logs \
		$(FULL_IMAGE):latest
	@echo "✅ Conteneur démarré sur http://localhost:8000"

stop:
	@echo "⏹️  Stopping $(CONTAINER_NAME)..."
	@docker stop $(CONTAINER_NAME) 2>/dev/null || echo "Container not running"
	@docker rm $(CONTAINER_NAME) 2>/dev/null || echo "Container not found"

logs:
	@echo "📋 Logs de $(CONTAINER_NAME):"
	docker logs -f $(CONTAINER_NAME)

test: run
	@echo "🧪 Testing image..."
	@sleep 5
	@if curl -f http://localhost:8000 > /dev/null 2>&1; then \
		echo "✅ Test réussi - Application accessible"; \
	else \
		echo "❌ Test échoué - Application non accessible"; \
		exit 1; \
	fi

clean:
	@echo "🧹 Cleaning up..."
	@docker stop $(CONTAINER_NAME) 2>/dev/null || true
	@docker rm $(CONTAINER_NAME) 2>/dev/null || true
	@docker rmi $(FULL_IMAGE):latest 2>/dev/null || true
	@docker rmi $(FULL_IMAGE):$(VERSION) 2>/dev/null || true
	@docker rmi $(FULL_IMAGE):v$(VERSION) 2>/dev/null || true
	@docker system prune -f
	@echo "✅ Nettoyage terminé"

all: hub-build run test

info:
	@echo "📊 Image Information:"
	@echo "Name: $(FULL_IMAGE)"
	@echo "Version: $(VERSION)"
	@echo "Size: $(shell docker images $(FULL_IMAGE):latest --format 'table {{.Size}}' | tail -n 1)"
	@echo "Created: $(shell docker images $(FULL_IMAGE):latest --format 'table {{.CreatedAt}}' | tail -n 1)" 