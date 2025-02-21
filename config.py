import os
from typing import Set, Dict, Any, Optional
from dataclasses import dataclass
import shutil
import subprocess

@dataclass
class Config:
    BASE_DIR: str = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER: str = os.path.join(BASE_DIR, "uploads")
    TEMP_FOLDER: str = os.path.join(UPLOAD_FOLDER, "temp")
    MAX_CONTENT_LENGTH: int = 512 * 1024 * 1024
    ALLOWED_IMAGE_EXTENSIONS: Set[str] = frozenset({'jpg', 'jpeg', 'png', 'gif', 'webp'})
    ALLOWED_VIDEO_EXTENSIONS: Set[str] = frozenset({'mp4', 'avi', 'mov', 'mkv', 'webm'})
    ALLOWED_MEDIA_EXTENSIONS: Set[str] = ALLOWED_VIDEO_EXTENSIONS | ALLOWED_IMAGE_EXTENSIONS
    YOUTUBE_DOWNLOAD_FOLDER: str = os.path.join(BASE_DIR, "downloads")
    YOUTUBE_MAX_DURATION: int = 3600
    LOG_FILE: str = os.path.join(BASE_DIR, "logs", "toolbox.log")
    CLEANUP_INTERVAL: int = 1800
    MAX_BATCH_SIZE: int = 20
    DEFAULT_QUALITY: int = 85
    CHUNK_SIZE: int = 8192
    FFMPEG_PATH: str = 'C:/ffmpeg/bin/ffmpeg.exe'
    
    @classmethod
    def get_ffmpeg_path(cls) -> Optional[str]:
        """Retourne le chemin vers FFmpeg"""
        paths_to_check = [
            'C:/ffmpeg/bin/ffmpeg.exe',  # Chemin Windows standard
            os.path.join(cls.BASE_DIR, "bin", "ffmpeg.exe"),
            os.path.join('C:', os.sep, 'ffmpeg', 'bin', 'ffmpeg.exe'),
            'ffmpeg'
        ]
        
        # Vérification directe des chemins
        for path in paths_to_check:
            if os.path.isfile(path):
                return path.replace('/', os.sep)
                
        # Recherche dans le PATH système
        system_ffmpeg = shutil.which('ffmpeg')
        if system_ffmpeg:
            return system_ffmpeg

        return None

    @classmethod
    def validate_ffmpeg(cls) -> bool:
        """Valide l'installation de FFmpeg"""
        ffmpeg_path = cls.get_ffmpeg_path()
        if not ffmpeg_path:
            return False
            
        try:
            result = subprocess.run([ffmpeg_path, "-version"], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE,
                                  timeout=5)
            return result.returncode == 0
        except Exception:
            return False

    @classmethod
    def validate(cls) -> None:
        """Valide la configuration et crée les dossiers nécessaires."""
        required_dirs = [
            cls.UPLOAD_FOLDER, 
            cls.TEMP_FOLDER,
            cls.YOUTUBE_DOWNLOAD_FOLDER,
            os.path.dirname(cls.LOG_FILE),
            os.path.join(cls.BASE_DIR, "bin")
        ]
        
        for directory in required_dirs:
            if not os.path.exists(directory):
                os.makedirs(directory)
                
        # Vérification de FFmpeg
        ffmpeg_path = cls.get_ffmpeg_path()
        if not ffmpeg_path:
            print("WARNING: FFmpeg non trouvé dans le système. Veuillez installer FFmpeg.")
            print("Téléchargement: https://www.ffmpeg.org/download.html")
            print("Une fois installé, assurez-vous que ffmpeg est dans le PATH")

    @classmethod
    def get_mime_types(cls) -> Dict[str, str]:
        """Retourne un mapping des extensions vers leurs types MIME."""
        return {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'mp4': 'video/mp4',
            'webm': 'video/webm',
            'avi': 'video/x-msvideo',
            'mov': 'video/quicktime',
            'mkv': 'video/x-matroska',
        }

    @classmethod
    def init_app(cls, app: Any) -> None:
        """Configuration optimisée de l'application"""
        cls.validate()
        app.config.from_object(cls)
        app.config['MAX_CONTENT_LENGTH'] = cls.MAX_CONTENT_LENGTH
        app.config['UPLOAD_FOLDER'] = cls.UPLOAD_FOLDER
        
        # Création des dossiers nécessaires en une seule passe
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(cls.TEMP_FOLDER, exist_ok=True)
        os.makedirs(os.path.dirname(cls.LOG_FILE), exist_ok=True)
