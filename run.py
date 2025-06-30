#!/usr/bin/env python3
"""
Toolbox Everything - Point d'entrée principal
==============================================

Script de lancement de l'application Flask avec support des arguments
de ligne de commande pour différents modes d'exécution.

Usage:
    python run.py [--dev] [--port PORT] [--host HOST]
"""

import argparse
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from flask_compress import Compress

from app.services.main import create_app

# Création de l'application au niveau module pour Gunicorn
app = create_app()


def setup_logging(app, debug_mode=False):
    """Configure le système de logging"""
    # Créer le dossier logs s'il n'existe pas
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Configuration du niveau de log
    log_level = logging.DEBUG if debug_mode else logging.INFO

    # Handler pour fichier avec rotation
    log_file = os.path.join(logs_dir, "toolbox.log")
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
    )
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
    )
    file_handler.setLevel(log_level)

    # Handler pour console (uniquement en mode debug)
    if debug_mode:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        console_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(console_handler)

    # Ajouter les handlers
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)

    # Log de démarrage
    app.logger.info("=== Toolbox Everything démarré ===")
    app.logger.info(f"Mode debug: {debug_mode}")
    app.logger.info(f"Niveau de log: {log_level}")


def create_argument_parser():
    """Crée le parser d'arguments de ligne de commande"""
    parser = argparse.ArgumentParser(
        description="Toolbox Everything - Collection d'outils pratiques",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python run.py                     # Mode production sur port 8000
  python run.py --dev               # Mode développement avec debug
  python run.py --port 5000         # Mode production sur port 5000
  python run.py --dev --port 3000   # Mode développement sur port 3000
        """,
    )

    parser.add_argument(
        "--dev",
        action="store_true",
        help="Lance en mode développement (debug activé, rechargement auto)",
    )

    parser.add_argument(
        "--port", type=int, default=8000, help="Port d'écoute du serveur (défaut: 8000)"
    )

    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Adresse d'écoute du serveur (défaut: 0.0.0.0)",
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Nombre de workers (uniquement en mode production avec gunicorn)",
    )

    parser.add_argument(
        "--version", action="version", version="Toolbox Everything v1.2.0"
    )

    return parser


def validate_args(args):
    """Valide les arguments fournis"""
    if args.port < 1 or args.port > 65535:
        print(f"Erreur: Le port doit être entre 1 et 65535 (fourni: {args.port})")
        sys.exit(1)

    if args.workers < 1:
        print(f"Erreur: Le nombre de workers doit être >= 1 (fourni: {args.workers})")
        sys.exit(1)


def main():
    """Point d'entrée principal"""
    # Parse des arguments
    parser = create_argument_parser()
    args = parser.parse_args()

    # Validation des arguments
    validate_args(args)

    # Configuration de la compression
    compress = Compress()
    compress.init_app(app)

    # Configuration du logging
    setup_logging(app, debug_mode=args.dev)

    # Affichage des informations de démarrage
    mode = "développement" if args.dev else "production"
    print(f"🚀 Démarrage de Toolbox Everything en mode {mode}")
    print(f"📍 Serveur: http://{args.host}:{args.port}")

    if args.dev:
        print("🔧 Mode développement activé:")
        print("   - Debug activé")
        print("   - Rechargement automatique")
        print("   - Logs détaillés")

    # Lancement du serveur
    try:
        if args.dev:
            # Mode développement avec le serveur Flask intégré
            app.run(
                host=args.host,
                port=args.port,
                debug=True,
                use_reloader=True,
                threaded=True,
            )
        else:
            # Mode production
            print(f"⚡ {args.workers} worker(s) configuré(s)")
            app.run(host=args.host, port=args.port, debug=False, threaded=True)

    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
