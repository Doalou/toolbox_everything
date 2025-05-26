"""
Exceptions personnalisées pour Toolbox Everything
"""
import logging
from typing import Optional, Dict, Any
from flask import jsonify, current_app
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

class ToolboxBaseException(Exception):
    """Exception de base pour tous les outils"""
    
    def __init__(self, message: str, error_code: str = "TOOLBOX_ERROR", 
                 status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'error': self.message,
            'error_code': self.error_code,
            'details': self.details
        }

class ValidationError(ToolboxBaseException):
    """Erreur de validation des données"""
    
    def __init__(self, message: str, field: str = None, **kwargs):
        super().__init__(message, "VALIDATION_ERROR", 400, **kwargs)
        if field:
            self.details['field'] = field

class FileProcessingError(ToolboxBaseException):
    """Erreur lors du traitement de fichiers"""
    
    def __init__(self, message: str, file_path: str = None, **kwargs):
        super().__init__(message, "FILE_PROCESSING_ERROR", 500, **kwargs)
        if file_path:
            self.details['file_path'] = file_path

class ConversionError(ToolboxBaseException):
    """Erreur lors de la conversion de média"""
    
    def __init__(self, message: str, format_from: str = None, format_to: str = None, **kwargs):
        super().__init__(message, "CONVERSION_ERROR", 500, **kwargs)
        if format_from:
            self.details['format_from'] = format_from
        if format_to:
            self.details['format_to'] = format_to

class YouTubeDownloadError(ToolboxBaseException):
    """Erreur lors du téléchargement YouTube"""
    
    def __init__(self, message: str, video_url: str = None, **kwargs):
        super().__init__(message, "YOUTUBE_DOWNLOAD_ERROR", 500, **kwargs)
        if video_url:
            self.details['video_url'] = video_url

class SecurityError(ToolboxBaseException):
    """Erreur de sécurité"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, "SECURITY_ERROR", 403, **kwargs)

class RateLimitError(ToolboxBaseException):
    """Erreur de limitation de débit"""
    
    def __init__(self, message: str = "Trop de requêtes", **kwargs):
        super().__init__(message, "RATE_LIMIT_ERROR", 429, **kwargs)

class ExternalServiceError(ToolboxBaseException):
    """Erreur avec un service externe"""
    
    def __init__(self, message: str, service_name: str = None, **kwargs):
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", 502, **kwargs)
        if service_name:
            self.details['service_name'] = service_name

def register_error_handlers(app):
    """Enregistre les gestionnaires d'erreurs globaux"""
    
    @app.errorhandler(ToolboxBaseException)
    def handle_toolbox_exception(error):
        logger.error(f"ToolboxException: {error.message}", extra=error.details)
        return jsonify(error.to_dict()), error.status_code
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        logger.warning(f"Validation error: {error.message}", extra=error.details)
        return jsonify(error.to_dict()), error.status_code
    
    @app.errorhandler(SecurityError)
    def handle_security_error(error):
        logger.error(f"Security error: {error.message}", extra=error.details)
        return jsonify(error.to_dict()), error.status_code
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'error': 'Ressource non trouvée',
            'error_code': 'NOT_FOUND'
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            'error': 'Erreur interne du serveur',
            'error_code': 'INTERNAL_ERROR'
        }), 500 