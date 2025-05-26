# Toolbox Everything

Une application web Flask fournissant une collection d'outils utiles.

## Services disponibles

- **YouTube Downloader**: Téléchargez des vidéos et de l'audio depuis YouTube.
- **Media Converter**: Convertissez des fichiers images et vidéos entre différents formats.
- **Essentials**: Une suite de petits outils pratiques :
    - Générateur de QR Code
    - Générateur de Mots de Passe
    - Analyseur de Texte
    - Générateur de Palette de Couleurs
    - Validateur d'URL
    - Calculateur de Hash
    - Encodeur/Décodeur Base64
    - Formateur JSON
    - Convertisseur de Timestamp

## Installation et Lancement

### Méthode standard

1.  **Prérequis**:
    *   Python 3.x
    *   pip
    *   FFmpeg (assurez-vous qu'il est dans votre PATH ou spécifiez le chemin dans `config.py`)

2.  **Cloner le dépôt (si applicable) ou télécharger les fichiers.**

3.  **Créer un environnement virtuel (recommandé)**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Pour Linux/macOS
    # .venv\Scripts\activate    # Pour Windows
    ```

4.  **Installer les dépendances**:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Lancer l'application**:
    ```bash
    python run.py
    ```
    L'application sera accessible par défaut sur `http://127.0.0.1:8000/`.

### Utilisation avec Docker

1.  **Prérequis**:
    *   Docker
    *   Docker Compose

2.  **Construire et démarrer l'application**:
    ```bash
    docker-compose up -d
    ```
    L'application sera accessible sur `http://localhost:8000/`.

3.  **Visualiser les logs**:
    ```bash
    docker-compose logs -f
    ```

4.  **Arrêter l'application**:
    ```bash
    docker-compose down
    ```

5.  **Reconstruire l'image après des modifications**:
    ```bash
    docker-compose up -d --build
    ```

### Volumes Docker

Les dossiers suivants sont montés comme volumes pour persister les données:
- `./uploads`: Fichiers téléversés temporairement
- `./downloads`: Fichiers téléchargés (ex: vidéos YouTube)
- `./logs`: Journaux d'application

## Structure du Projet

- `run.py`: Point d'entrée de l'application.
- `config.py`: Fichier de configuration.
- `requirements.txt`: Liste des dépendances Python.
- `app/`: Répertoire principal de l'application Flask.
  - `core/`: Logique métier centrale, sécurité, exceptions.
  - `services/`: Contient les blueprints pour chaque service principal.
    - `common/`: Utilitaires partagés entre les services.
    - `essentials/`: Outils essentiels (QR code, mot de passe, etc.).
    - `media_converter/`: Service de conversion de médias.
    - `youtube_downloader/`: Service de téléchargement YouTube.
  - `static/`: Fichiers statiques (CSS, JavaScript, images).
  - `templates/`: Modèles HTML Jinja2.
    - `errors/`: Pages d'erreur personnalisées.
    - `essentials/`: Templates pour les outils essentiels.
- `uploads/`: Répertoire pour les fichiers téléversés temporairement.
- `downloads/`: Répertoire pour les fichiers téléchargés (ex: YouTube).
