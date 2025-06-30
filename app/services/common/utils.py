import os
import logging
import shutil
from typing import Union, Optional, Callable, Any
from pathlib import Path
import hashlib
from datetime import datetime
import logging.handlers
import functools
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class FileOperationError(Exception):
    pass

def setup_logger(log_file: str = 'toolbox.log', level: int = logging.INFO) -> None:
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10_485_760, backupCount=5
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)

def log_message(msg: str, level: str = 'info') -> None:
    log_methods = {
        'debug': logger.debug,
        'info': logger.info,
        'warning': logger.warning,
        'error': logger.error,
        'critical': logger.critical
    }
    log_method = log_methods.get(level.lower(), logger.info)
    log_method(msg)

def safe_remove_file(file_path: Union[str, Path]) -> bool:
    try:
        path = Path(file_path)
        if path.exists():
            if path.is_file():
                path.unlink()
                log_message(f"Fichier supprimé avec succès: {file_path}")
                return True
            else:
                raise FileOperationError(f"Le chemin existe mais n'est pas un fichier: {file_path}")
        return False
    except Exception as e:
        log_message(f"Erreur lors de la suppression du fichier {file_path}: {e}", 'error')
        raise FileOperationError(f"Erreur lors de la suppression: {e}")

def ensure_dir(path: Union[str, Path]) -> Path:
    try:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    except Exception as e:
        log_message(f"Erreur lors de la création du répertoire {path}: {e}", 'error')
        raise FileOperationError(f"Impossible de créer le répertoire: {e}")

def get_file_hash(file_path: Union[str, Path], algorithm: str = 'sha256') -> str:
    hash_algorithms = {
        'md5': hashlib.md5(),
        'sha1': hashlib.sha1(),
        'sha256': hashlib.sha256()
    }
    
    try:
        hasher = hash_algorithms.get(algorithm.lower())
        if not hasher:
            raise ValueError(f"Algorithme de hash non supporté: {algorithm}")
            
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        log_message(f"Erreur lors du calcul du hash pour {file_path}: {e}", 'error')
        raise FileOperationError(f"Impossible de calculer le hash: {e}")

def create_unique_filename(original_name: str, directory: Union[str, Path]) -> Path:
    directory = Path(directory)
    name, ext = os.path.splitext(original_name)
    counter = 1
    new_path = directory / f"{name}{ext}"
    
    while new_path.exists():
        new_path = directory / f"{name}_{counter}{ext}"
        counter += 1
    
    return new_path

def safe_copy_file(src: Union[str, Path], dst: Union[str, Path], overwrite: bool = False) -> bool:
    try:
        src_path = Path(src)
        dst_path = Path(dst)
        
        if not src_path.exists():
            raise FileOperationError(f"Le fichier source n'existe pas: {src}")
            
        if dst_path.exists() and not overwrite:
            raise FileOperationError(f"Le fichier de destination existe déjà: {dst}")
            
        shutil.copy2(src_path, dst_path)
        return True
    except Exception as e:
        log_message(f"Erreur lors de la copie de {src} vers {dst}: {e}", 'error')
        raise FileOperationError(f"Erreur lors de la copie: {e}")

def get_file_info(file_path: Union[str, Path]) -> dict:
    try:
        path = Path(file_path)
        stats = path.stat()
        return {
            'name': path.name,
            'extension': path.suffix,
            'size': stats.st_size,
            'created': datetime.fromtimestamp(stats.st_ctime),
            'modified': datetime.fromtimestamp(stats.st_mtime),
            'accessed': datetime.fromtimestamp(stats.st_atime),
            'is_file': path.is_file(),
            'is_dir': path.is_dir(),
            'path': str(path.absolute())
        }
    except Exception as e:
        log_message(f"Erreur lors de la récupération des informations pour {file_path}: {e}", 'error')
        raise FileOperationError(f"Impossible d'obtenir les informations du fichier: {e}")

def retry_operation(retries: int = 3, delay: float = 1.0) -> Callable:
    """Décorateur pour réessayer une opération plusieurs fois."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if i < retries - 1:
                        time.sleep(delay)
            raise last_error
        return wrapper
    return decorator

async def async_file_operation(file_path: Union[str, Path], 
                             operation: Callable,
                             executor: Optional[ThreadPoolExecutor] = None) -> Any:
    """Exécute une opération de fichier de manière asynchrone."""
    loop = asyncio.get_event_loop()
    if executor is None:
        executor = ThreadPoolExecutor()
    return await loop.run_in_executor(executor, operation, file_path)

class ResourceManager:
    """Gestionnaire de ressources avec nettoyage automatique."""
    def __init__(self, cleanup_callback: Optional[Callable] = None):
        self.resources = set()
        self.cleanup_callback = cleanup_callback

    def add(self, resource: Any) -> None:
        self.resources.add(resource)

    def remove(self, resource: Any) -> None:
        self.resources.discard(resource)

    def cleanup(self) -> None:
        for resource in self.resources.copy():
            try:
                if self.cleanup_callback:
                    self.cleanup_callback(resource)
                self.remove(resource)
            except Exception as e:
                log_message(f"Erreur lors du nettoyage de {resource}: {e}", 'error')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

def validate_file_size(file_path: Union[str, Path], max_size: int) -> bool:
    """Valide la taille d'un fichier."""
    return Path(file_path).stat().st_size <= max_size

def sanitize_filename(filename: str) -> str:
    """Nettoie et sécurise un nom de fichier."""
    import re
    clean_name = re.sub(r'[^\w\-_\. ]', '_', filename)
    return clean_name[:255]
