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

class SecurityManager:
    """Gestionnaire de sécurité centralisé"""
    
    DANGEROUS_EXTENSIONS = {
        'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'vbe', 'ws', 'wsf',
        'wsh', 'ps1', 'ps1xml', 'ps2', 'ps2xml', 'psc1', 'psc2', 'msh', 'msh1',
        'msh2', 'mshxml', 'msh1xml', 'msh2xml', 'jar', 'js', 'jse', 'wsc', 'wsf'
    }
    
    MAX_FILENAME_LENGTH = 255
    ALLOWED_CHARS_PATTERN = re.compile(r'^[a-zA-Z0-9._\-\s]+$')
    
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
    def validate_file_content(cls, file_path: str, expected_mime_type: str = None) -> bool:
        """Valide le contenu d'un fichier via son type MIME"""
        try:
            actual_mime_type, _ = mimetypes.guess_type(file_path)
            
            if expected_mime_type and actual_mime_type != expected_mime_type:
                raise SecurityError(
                    f"Type MIME inattendu: {actual_mime_type}, attendu: {expected_mime_type}"
                )
                
            return True
        except Exception as e:
            raise SecurityError(f"Erreur lors de la validation du contenu: {str(e)}")
    
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

def validate_file_upload(allowed_extensions: set = None, max_size_mb: int = 100):
    """Décorateur pour valider les uploads de fichiers"""
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
            
            # Valider l'extension
            if allowed_extensions:
                SecurityManager.validate_file_extension(secure_name, allowed_extensions)
            
            # Ajouter le nom sécurisé à la requête
            g.secure_filename = secure_name
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator 