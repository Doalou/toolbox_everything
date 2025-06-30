"""
Module de sécurité pour Toolbox Everything
"""
import os
import re
import hashlib
import secrets
import mimetypes
from typing import Optional, List, Dict, Any
from functools import wraps
from flask import request, current_app, g
from werkzeug.utils import secure_filename
from pathlib import Path

from .exceptions import SecurityError, ValidationError

# Import optionnel de python-magic pour validation MIME robuste
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    try:
        import filetype
        FILETYPE_AVAILABLE = True
    except ImportError:
        FILETYPE_AVAILABLE = False

class SecurityManager:
    """Gestionnaire de sécurité centralisé"""
    
    DANGEROUS_EXTENSIONS = {
        'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'vbe', 'ws', 'wsf',
        'wsh', 'ps1', 'ps1xml', 'ps2', 'ps2xml', 'psc1', 'psc2', 'msh', 'msh1',
        'msh2', 'mshxml', 'msh1xml', 'msh2xml', 'jar', 'js', 'jse', 'wsc', 'wsf'
    }
    
    MAX_FILENAME_LENGTH = 255
    ALLOWED_CHARS_PATTERN = re.compile(r'^[a-zA-Z0-9._\-\s]+$')
    
    # Mapping des extensions vers types MIME autorisés
    SECURE_MIME_MAPPING = {
        'jpg': ['image/jpeg'],
        'jpeg': ['image/jpeg'],
        'png': ['image/png'],
        'gif': ['image/gif'],
        'webp': ['image/webp'],
        'mp4': ['video/mp4'],
        'webm': ['video/webm'],
        'avi': ['video/x-msvideo', 'video/avi'],
        'mov': ['video/quicktime'],
        'mkv': ['video/x-matroska'],
        'pdf': ['application/pdf'],
        'txt': ['text/plain'],
        'json': ['application/json', 'text/json']
    }
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Nettoie et sécurise un nom de fichier"""
        if not filename:
            raise ValidationError("Nom de fichier vide")
            
        # Nettoyer avec secure_filename de Werkzeug
        clean_name = secure_filename(filename)
        
        if not clean_name:
            raise ValidationError("Nom de fichier invalide après nettoyage")
            
        # Vérifier la longueur
        if len(clean_name) > cls.MAX_FILENAME_LENGTH:
            name, ext = os.path.splitext(clean_name)
            clean_name = name[:cls.MAX_FILENAME_LENGTH - len(ext)] + ext
            
        return clean_name
    
    @classmethod
    def validate_file_extension(cls, filename: str, allowed_extensions: set) -> bool:
        """Valide l'extension d'un fichier"""
        if not filename:
            return False
            
        ext = Path(filename).suffix.lower().lstrip('.')
        
        # Vérifier si l'extension est dangereuse
        if ext in cls.DANGEROUS_EXTENSIONS:
            raise SecurityError(f"Extension de fichier dangereuse: .{ext}")
            
        # Vérifier si l'extension est autorisée
        if allowed_extensions and ext not in allowed_extensions:
            raise ValidationError(f"Extension non autorisée: .{ext}")
            
        return True
    
    @classmethod
    def detect_file_type(cls, file_path: str) -> Optional[str]:
        """Détecte le type MIME réel d'un fichier"""
        if not os.path.exists(file_path):
            return None
            
        # Méthode 1: python-magic (le plus fiable)
        if MAGIC_AVAILABLE:
            try:
                mime = magic.Magic(mime=True)
                return mime.from_file(file_path)
            except Exception as e:
                current_app.logger.warning(f"Erreur python-magic: {e}")
        
        # Méthode 2: filetype (alternatif fiable)
        if FILETYPE_AVAILABLE:
            try:
                kind = filetype.guess(file_path)
                if kind:
                    return kind.mime
            except Exception as e:
                current_app.logger.warning(f"Erreur filetype: {e}")
        
        # Méthode 3: fallback avec mimetypes (moins fiable)
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type
    
    @classmethod
    def validate_file_content(cls, file_path: str, expected_extension: str = None) -> bool:
        """Valide le contenu d'un fichier via son type MIME réel"""
        try:
            actual_mime_type = cls.detect_file_type(file_path)
            
            if not actual_mime_type:
                raise SecurityError("Impossible de déterminer le type de fichier")
            
            # Si on a une extension attendue, vérifier la cohérence
            if expected_extension:
                ext = expected_extension.lower().lstrip('.')
                expected_mimes = cls.SECURE_MIME_MAPPING.get(ext, [])
                
                if expected_mimes and actual_mime_type not in expected_mimes:
                    raise SecurityError(
                        f"Type MIME détecté ({actual_mime_type}) ne correspond pas "
                        f"à l'extension .{ext} (attendu: {', '.join(expected_mimes)})"
                    )
            
            # Vérifications spécifiques selon le type
            if actual_mime_type.startswith('text/'):
                # Pour les fichiers texte, vérifier qu'il n'y a pas de contenu binaire suspect
                with open(file_path, 'rb') as f:
                    chunk = f.read(1024)
                    # Vérifier la présence de bytes NULL ou de caractères de contrôle suspects
                    if b'\x00' in chunk or any(b < 0x09 or (0x0E <= b <= 0x1F) for b in chunk):
                        raise SecurityError("Fichier texte contenant des données binaires suspectes")
            
            return True
            
        except Exception as e:
            if isinstance(e, SecurityError):
                raise
            raise SecurityError(f"Erreur lors de la validation du contenu: {str(e)}")
    
    @classmethod
    def validate_file_size(cls, file_path: str, max_size_mb: int = 100) -> bool:
        """Valide la taille d'un fichier"""
        try:
            file_size = os.path.getsize(file_path)
            max_size_bytes = max_size_mb * 1024 * 1024
            
            if file_size > max_size_bytes:
                raise ValidationError(f"Fichier trop volumineux: {file_size} bytes (max: {max_size_bytes} bytes)")
            
            return True
        except OSError as e:
            raise SecurityError(f"Erreur lors de la vérification de la taille: {str(e)}")
    
    @classmethod
    def comprehensive_file_validation(cls, file_path: str, allowed_extensions: set = None, 
                                    max_size_mb: int = 100) -> Dict[str, Any]:
        """Validation complète d'un fichier uploadé"""
        filename = os.path.basename(file_path)
        ext = Path(filename).suffix.lower().lstrip('.')
        
        validation_result = {
            'valid': False,
            'filename': filename,
            'extension': ext,
            'detected_mime': None,
            'file_size': 0,
            'errors': [],
            'warnings': []
        }
        
        try:
            # 1. Validation du nom de fichier
            cls.sanitize_filename(filename)
            
            # 2. Validation de l'extension
            if allowed_extensions:
                cls.validate_file_extension(filename, allowed_extensions)
            
            # 3. Validation de la taille
            cls.validate_file_size(file_path, max_size_mb)
            validation_result['file_size'] = os.path.getsize(file_path)
            
            # 4. Validation du contenu MIME
            detected_mime = cls.detect_file_type(file_path)
            validation_result['detected_mime'] = detected_mime
            
            if detected_mime:
                cls.validate_file_content(file_path, ext)
            else:
                validation_result['warnings'].append("Type MIME non détectable")
            
            validation_result['valid'] = True
            
        except (SecurityError, ValidationError) as e:
            validation_result['errors'].append(str(e))
        except Exception as e:
            validation_result['errors'].append(f"Erreur inattendue: {str(e)}")
        
        return validation_result
    
    @classmethod
    def generate_secure_token(cls, length: int = 32) -> str:
        """Génère un token sécurisé"""
        return secrets.token_urlsafe(length)
    
    @classmethod
    def hash_password(cls, password: str, salt: str = None) -> tuple:
        """Hash un mot de passe avec un sel"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        pwdhash = hashlib.pbkdf2_hmac('sha256',
                                     password.encode('utf-8'),
                                     salt.encode('utf-8'),
                                     100000)
        
        return pwdhash.hex(), salt

class RateLimiter:
    """Limiteur de débit simple en mémoire"""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Vérifie si une requête est autorisée"""
        import time
        
        now = time.time()
        window_start = now - window_seconds
        
        # Nettoyer les anciennes entrées
        if key in self.requests:
            self.requests[key] = [req_time for req_time in self.requests[key] 
                                if req_time > window_start]
        else:
            self.requests[key] = []
        
        # Vérifier la limite
        if len(self.requests[key]) >= max_requests:
            return False
        
        # Ajouter la requête actuelle
        self.requests[key].append(now)
        return True

# Instance globale du limiteur de débit
rate_limiter = RateLimiter()

def require_rate_limit(max_requests: int = 10, window_seconds: int = 60):
    """Décorateur pour limiter le débit des requêtes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.environ.get('REMOTE_ADDR', 'unknown')
            key = f"{f.__name__}:{client_ip}"
            
            if not rate_limiter.is_allowed(key, max_requests, window_seconds):
                raise SecurityError("Trop de requêtes")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_request_size(max_size_mb: int = 100):
    """Décorateur pour valider la taille de la requête"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            content_length = request.content_length
            max_size_bytes = max_size_mb * 1024 * 1024
            
            if content_length and content_length > max_size_bytes:
                raise ValidationError(f"Fichier trop volumineux (max: {max_size_mb}MB)")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def secure_headers(f):
    """Décorateur pour ajouter des en-têtes de sécurité"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        
        # Ajouter les en-têtes de sécurité
        if hasattr(response, 'headers'):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['Content-Security-Policy'] = "default-src 'self'"
        
        return response
    return decorated_function

def validate_file_upload(allowed_extensions: set = None, max_size_mb: int = 100, 
                        validate_content: bool = True):
    """Décorateur pour valider les uploads de fichiers avec validation MIME"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'file' not in request.files:
                raise ValidationError("Aucun fichier fourni")
            
            file = request.files['file']
            if not file or not file.filename:
                raise ValidationError("Fichier invalide")
            
            # Valider le nom de fichier
            secure_name = SecurityManager.sanitize_filename(file.filename)
            
            # Sauvegarder temporairement pour validation du contenu
            temp_path = None
            try:
                if validate_content:
                    import tempfile
                    temp_fd, temp_path = tempfile.mkstemp()
                    os.close(temp_fd)
                    file.save(temp_path)
                    
                    # Validation complète
                    validation_result = SecurityManager.comprehensive_file_validation(
                        temp_path, allowed_extensions, max_size_mb
                    )
                    
                    if not validation_result['valid']:
                        raise SecurityError(f"Fichier non valide: {'; '.join(validation_result['errors'])}")
                    
                    # Ajouter les informations de validation à g
                    g.file_validation = validation_result
                    
                    # Repositionner le curseur du fichier
                    file.seek(0)
                else:
                    # Validation basique seulement
                    if allowed_extensions:
                        SecurityManager.validate_file_extension(secure_name, allowed_extensions)
            
            finally:
                # Nettoyer le fichier temporaire
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except OSError:
                        pass
            
            # Ajouter le nom sécurisé à la requête
            g.secure_filename = secure_name
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator 