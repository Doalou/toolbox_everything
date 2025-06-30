# =====================================
# Toolbox Everything - Makefile
# =====================================

# Variables
PYTHON := python3
PIP := pip3
FLASK_APP := run.py
PORT := 8000

# Couleurs pour l'affichage
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

.PHONY: help install dev run build clean test lint format security check docker-build docker-run

# Affichage de l'aide
help:
	@echo "$(GREEN)Toolbox Everything - Commandes disponibles:$(NC)"
	@echo ""
	@echo "  $(YELLOW)setup$(NC)         - Installation complète (dépendances + configuration)"
	@echo "  $(YELLOW)install$(NC)       - Installation des dépendances"
	@echo "  $(YELLOW)dev$(NC)           - Lancement en mode développement"
	@echo "  $(YELLOW)run$(NC)           - Lancement en mode production"
	@echo "  $(YELLOW)build$(NC)         - Construction de l'application"
	@echo "  $(YELLOW)clean$(NC)         - Nettoyage des fichiers temporaires"
	@echo "  $(YELLOW)test$(NC)          - Exécution des tests"
	@echo "  $(YELLOW)lint$(NC)          - Vérification du code (flake8)"
	@echo "  $(YELLOW)format$(NC)        - Formatage du code (black)"
	@echo "  $(YELLOW)security$(NC)      - Vérification de sécurité (bandit)"
	@echo "  $(YELLOW)check$(NC)         - Vérifications complètes (lint + security)"
	@echo "  $(YELLOW)docker-build$(NC)  - Construction de l'image Docker"
	@echo "  $(YELLOW)docker-run$(NC)    - Lancement du conteneur Docker"
	@echo ""

# Installation complète
setup: install
	@echo "$(GREEN)✓ Configuration de l'environnement...$(NC)"
	@mkdir -p logs uploads downloads
	@echo "$(GREEN)✓ Installation terminée !$(NC)"

# Installation des dépendances
install:
	@echo "$(YELLOW)Installation des dépendances...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dépendances installées$(NC)"

# Mode développement
dev:
	@echo "$(YELLOW)Lancement en mode développement...$(NC)"
	@echo "$(GREEN)Serveur accessible sur http://localhost:$(PORT)$(NC)"
	$(PYTHON) $(FLASK_APP) --dev --port $(PORT)

# Mode production
run:
	@echo "$(YELLOW)Lancement en mode production...$(NC)"
	@echo "$(GREEN)Serveur accessible sur http://localhost:$(PORT)$(NC)"
	$(PYTHON) $(FLASK_APP) --port $(PORT)

# Construction
build: clean install
	@echo "$(GREEN)✓ Application construite$(NC)"

# Nettoyage
clean:
	@echo "$(YELLOW)Nettoyage des fichiers temporaires...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/
	rm -rf uploads/temp/* downloads/temp/* logs/*.log
	@echo "$(GREEN)✓ Nettoyage terminé$(NC)"

# Tests
test:
	@echo "$(YELLOW)Exécution des tests...$(NC)"
	@if [ -d "tests" ]; then \
		$(PYTHON) -m pytest tests/ -v; \
	else \
		echo "$(RED)Aucun dossier de tests trouvé$(NC)"; \
	fi

# Vérification du code
lint:
	@echo "$(YELLOW)Vérification du code avec flake8...$(NC)"
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 app/ --max-line-length=100 --ignore=E203,W503; \
		echo "$(GREEN)✓ Code vérifié$(NC)"; \
	else \
		echo "$(RED)flake8 non installé. Installation: pip install flake8$(NC)"; \
	fi

# Formatage du code
format:
	@echo "$(YELLOW)Formatage du code avec black...$(NC)"
	@if command -v black >/dev/null 2>&1; then \
		black app/ --line-length=100; \
		echo "$(GREEN)✓ Code formaté$(NC)"; \
	else \
		echo "$(RED)black non installé. Installation: pip install black$(NC)"; \
	fi

# Vérification de sécurité
security:
	@echo "$(YELLOW)Vérification de sécurité avec bandit...$(NC)"
	@if command -v bandit >/dev/null 2>&1; then \
		bandit -r app/ -f json -o security-report.json || true; \
		bandit -r app/ --exclude=*/tests/*; \
		echo "$(GREEN)✓ Vérification de sécurité terminée$(NC)"; \
	else \
		echo "$(RED)bandit non installé. Installation: pip install bandit$(NC)"; \
	fi

# Vérifications complètes
check: lint security
	@echo "$(GREEN)✓ Toutes les vérifications sont terminées$(NC)"

# Construction Docker
docker-build:
	@echo "$(YELLOW)Construction de l'image Docker...$(NC)"
	docker build -t toolbox-everything:latest .
	@echo "$(GREEN)✓ Image Docker construite$(NC)"

# Lancement Docker
docker-run:
	@echo "$(YELLOW)Lancement du conteneur Docker...$(NC)"
	@echo "$(GREEN)Serveur accessible sur http://localhost:$(PORT)$(NC)"
	docker run -p $(PORT):8000 --rm -it toolbox-everything:latest

# Vérification des dépendances
deps-check:
	@echo "$(YELLOW)Vérification des dépendances...$(NC)"
	@if command -v pip-audit >/dev/null 2>&1; then \
		pip-audit; \
	else \
		echo "$(RED)pip-audit non installé. Installation: pip install pip-audit$(NC)"; \
	fi

# Mise à jour des dépendances
deps-update:
	@echo "$(YELLOW)Mise à jour des dépendances...$(NC)"
	$(PIP) install --upgrade -r requirements.txt
	@echo "$(GREEN)✓ Dépendances mises à jour$(NC)"

# Génération du fichier requirements.txt
freeze:
	@echo "$(YELLOW)Génération du fichier requirements.txt...$(NC)"
	$(PIP) freeze > requirements-freeze.txt
	@echo "$(GREEN)✓ Fichier requirements-freeze.txt généré$(NC)" 