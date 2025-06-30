"""
Toolbox Everything - Application Flask
======================================

Une collection d'outils pratiques pour vos besoins quotidiens :
- YouTube Downloader
- Convertisseur Média
- Outils Essentiels (QR Code, mots de passe, etc.)
- Système PDF (bientôt)

Version: 1.2.0
"""

__version__ = "1.2.0"
__author__ = "Toolbox Everything Team"
__license__ = "MIT"

from .services.main import create_app

# Export de la fonction principale
__all__ = ["create_app"]
