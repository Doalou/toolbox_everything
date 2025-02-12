import os
from typing import Set, Dict, Any
from dataclasses import dataclass

@dataclass
class Config:
    BASE_DIR: str = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER: str = os.path.join(BASE_DIR, "uploads")
    TEMP_FOLDER: str = os.path.join(UPLOAD_FOLDER, "temp")
    MAX_CONTENT_LENGTH: int = 512 * 1024 * 1024
    ALLOWED_IMAGE_EXTENSIONS: Set[str] = frozenset({'png', 'jpg', 'jpeg', 'gif', 'webp'})
    ALLOWED_VIDEO_EXTENSIONS: Set[str] = frozenset({'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm'})
    YOUTUBE_DOWNLOAD_FOLDER: str = os.path.join(BASE_DIR, "downloads")
    YOUTUBE_MAX_DURATION: int = 3600
    LOG_FILE: str = os.path.join(BASE_DIR, "logs", "toolbox.log")
    CLEANUP_INTERVAL: int = 3600
    MAX_BATCH_SIZE: int = 10
    DEFAULT_QUALITY: int = 85
    
    @classmethod
    def validate(cls) -> None:
        """Valide la configuration et crée les dossiers nécessaires."""
        required_dirs = [cls.UPLOAD_FOLDER, cls.TEMP_FOLDER, 
                        cls.YOUTUBE_DOWNLOAD_FOLDER, os.path.dirname(cls.LOG_FILE)]
        
        for directory in required_dirs:
            if not os.path.exists(directory):
                os.makedirs(directory)

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
        """Initialise l'application avec la configuration."""
        cls.validate()
        app.config.from_object(cls)
        
        # Configuration du logging
        if not os.path.exists(os.path.dirname(cls.LOG_FILE)):
            os.makedirs(os.path.dirname(cls.LOG_FILE))
