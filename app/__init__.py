"""
Toolbox Everything - Application Flask
======================================

Une collection d'outils pratiques pour vos besoins quotidiens :
- YouTube Downloader
- Convertisseur Média
- Outils Essentiels (QR Code, mots de passe, etc.)
- Outils PDF (150+ opérations via Stirling PDF)
"""

import os

from dotenv import load_dotenv

load_dotenv()

__version__ = os.environ.get("APP_VERSION", "0.0.0")
__author__ = "Doalou"
__license__ = "MIT"

from .services.main import create_app

__all__ = ["create_app"]
