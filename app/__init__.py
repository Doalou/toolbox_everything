"""
Toolbox Everything - Application Flask
======================================

Une collection d'outils pratiques pour vos besoins quotidiens :
- Downloader vidéo / audio (YouTube, Vimeo, Dailymotion, TikTok)
- Convertisseur Média
- Outils Essentiels (QR Code, mots de passe, etc.)
- Outils PDF et speedtest
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _read_version() -> str:
    version_file = Path(__file__).resolve().parent.parent / "VERSION"
    if version_file.exists():
        return version_file.read_text(encoding="utf-8").strip()
    return "1.3.1"


__version__ = os.environ.get("APP_VERSION", _read_version())
__author__ = "Doalou"
__license__ = "MIT"

from .services.main import create_app

__all__ = ["create_app"]
