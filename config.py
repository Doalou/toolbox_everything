"""
Configuration globale de Toolbox Everything.

Centralise chemins, limites, et quelques listes blanches. La détection FFmpeg
est ici la seule source de vérité — plus de duplication dans `main.py` ou
dans le blueprint YouTube.
"""

from __future__ import annotations

import os
import secrets
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, FrozenSet, Optional

_DEFAULT_SECRET = "your-secret-key-change-this-in-production"  # noqa: S105


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


@dataclass
class Config:
    BASE_DIR: str = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY: str = os.environ.get("SECRET_KEY", _DEFAULT_SECRET)

    UPLOAD_FOLDER: str = os.path.join(BASE_DIR, "uploads")
    TEMP_FOLDER: str = os.path.join(UPLOAD_FOLDER, "temp")
    YOUTUBE_DOWNLOAD_FOLDER: str = os.path.join(BASE_DIR, "downloads")
    LOG_FILE: str = os.path.join(BASE_DIR, "logs", "toolbox.log")

    MAX_CONTENT_LENGTH: int = _env_int("MAX_CONTENT_LENGTH", 512 * 1024 * 1024)
    YOUTUBE_MAX_DURATION: int = _env_int("YOUTUBE_MAX_DURATION", 3600)
    CLEANUP_INTERVAL: int = 1800
    MAX_BATCH_SIZE: int = 20
    DEFAULT_QUALITY: int = 85
    CHUNK_SIZE: int = 8192

    ALLOWED_IMAGE_EXTENSIONS: FrozenSet[str] = frozenset(
        {"jpg", "jpeg", "png", "gif", "webp"}
    )
    ALLOWED_VIDEO_EXTENSIONS: FrozenSet[str] = frozenset(
        {"mp4", "avi", "mov", "mkv", "webm"}
    )
    ALLOWED_MEDIA_EXTENSIONS: FrozenSet[str] = (
        ALLOWED_VIDEO_EXTENSIONS | ALLOWED_IMAGE_EXTENSIONS
    )

    # Domaines autorisés par le validator d'URL (unique source, consommée
    # dans `services/essentials/tools.py`).
    URL_VALIDATOR_ALLOWED_DOMAINS: FrozenSet[str] = frozenset(
        {
            "google.com",
            "www.google.com",
            "github.com",
            "www.github.com",
            "stackoverflow.com",
            "www.stackoverflow.com",
            "wikipedia.org",
            "en.wikipedia.org",
            "fr.wikipedia.org",
            "python.org",
            "www.python.org",
            "mozilla.org",
            "www.mozilla.org",
            "cloudflare.com",
            "www.cloudflare.com",
            "example.com",
            "www.example.com",
        }
    )
    URL_VALIDATOR_ALLOWED_DOMAIN_SUFFIXES: FrozenSet[str] = frozenset(
        {
            ".google.com",
            ".github.com",
            ".stackoverflow.com",
            ".wikipedia.org",
            ".python.org",
            ".mozilla.org",
            ".cloudflare.com",
        }
    )

    @classmethod
    def get_ffmpeg_path(cls) -> Optional[str]:
        """Résolution unique de FFmpeg (PATH → chemins connus → None)."""
        env_path = os.environ.get("FFMPEG_PATH")
        if env_path and os.path.isfile(env_path):
            return env_path

        ffmpeg_which = shutil.which("ffmpeg")
        if ffmpeg_which:
            return ffmpeg_which

        candidates = [
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            os.path.join(cls.BASE_DIR, "bin", "ffmpeg.exe"),
            os.path.join(cls.BASE_DIR, "bin", "ffmpeg"),
        ]
        for path in candidates:
            if os.path.isfile(path):
                return path
        return None

    @classmethod
    def validate_ffmpeg(cls) -> bool:
        ffmpeg_path = cls.get_ffmpeg_path()
        if not ffmpeg_path:
            return False
        try:
            result = subprocess.run(
                [ffmpeg_path, "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
                check=False,
            )
            return result.returncode == 0
        except Exception:  # noqa: BLE001
            return False

    @classmethod
    def get_mime_types(cls) -> Dict[str, str]:
        return {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "gif": "image/gif",
            "webp": "image/webp",
            "mp4": "video/mp4",
            "webm": "video/webm",
            "avi": "video/x-msvideo",
            "mov": "video/quicktime",
            "mkv": "video/x-matroska",
            "pdf": "application/pdf",
        }

    @classmethod
    def _ensure_secret_key(cls) -> str:
        if cls.SECRET_KEY == _DEFAULT_SECRET:
            generated = secrets.token_hex(32)
            cls.SECRET_KEY = generated
            print(
                "\033[33m⚠  SECRET_KEY non configurée — clé aléatoire générée "
                "pour cette session.\033[0m"
            )
            print(
                "\033[33m   Pour la rendre persistante, ajoutez dans votre .env :\033[0m"
            )
            print(f"\033[33m   SECRET_KEY={generated}\033[0m")
        return cls.SECRET_KEY

    @classmethod
    def _ensure_dirs(cls) -> None:
        for directory in (
            cls.UPLOAD_FOLDER,
            cls.TEMP_FOLDER,
            cls.YOUTUBE_DOWNLOAD_FOLDER,
            os.path.dirname(cls.LOG_FILE),
        ):
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

    @classmethod
    def init_app(cls, app: Any) -> None:
        cls._ensure_secret_key()
        cls._ensure_dirs()
        app.config.from_object(cls)
        app.config["MAX_CONTENT_LENGTH"] = cls.MAX_CONTENT_LENGTH
        app.config["UPLOAD_FOLDER"] = cls.UPLOAD_FOLDER

        # Exposer FFmpeg pour les blueprints (si détecté).
        ffmpeg_path = cls.get_ffmpeg_path()
        if ffmpeg_path:
            app.config["FFMPEG_PATH"] = ffmpeg_path
        elif not os.environ.get("DOCKER_ENV"):
            print(
                "\033[33m⚠  FFmpeg introuvable. Installation : "
                "https://www.ffmpeg.org/download.html\033[0m"
            )
