from flask import Flask, render_template, request, g, abort, redirect, url_for
import logging
import time
from typing import Optional
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.exceptions import HTTPException
from logging.handlers import RotatingFileHandler
from config import Config
from .youtube_downloader.routes import youtube_bp
from .media_converter.routes import media_bp

def create_app(config_class: Optional[object] = None) -> Flask:
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configuration
    app.config.from_object(config_class or Config)
    Config.init_app(app)
    
    # Middleware pour gérer les en-têtes de proxy
    app.wsgi_app = ProxyFix(app.wsgi_app)
    
    # Configuration du logging
    if not app.debug:
        file_handler = RotatingFileHandler('toolbox.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Toolbox startup')

    # Blueprints
    app.register_blueprint(youtube_bp, url_prefix="/youtube")
    app.register_blueprint(media_bp, url_prefix="/media")

    # Ajouter une route racine pour youtube
    @app.route("/youtube")
    def youtube():
        return redirect(url_for('youtube.index'))

    @app.before_request
    def before_request():
        g.start_time = time.time()
        if not request.path.startswith('/static'):
            app.logger.info(f'Request: {request.method} {request.url}')

    @app.before_request
    def validate_request():
        # Vérification des en-têtes
        if request.method != 'OPTIONS':
            user_agent = request.headers.get('User-Agent', '')
            if not user_agent or len(user_agent) > 500:
                abort(400, "Invalid User-Agent header")
            
            # Vérification du Content-Type pour les POST
            if request.method == 'POST' and request.headers.get('Content-Type'):
                content_type = request.headers['Content-Type'].lower()
                valid_types = ['application/json', 'multipart/form-data', 
                             'application/x-www-form-urlencoded']
                if not any(valid_type in content_type for valid_type in valid_types):
                    abort(400, "Invalid Content-Type")

    @app.after_request
    def after_request(response):
        if not request.path.startswith('/static'):
            diff = time.time() - g.start_time
            app.logger.info(f'Response time: {diff:.2f}s')
        return response

    # Gestion des erreurs globale
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f'Unhandled exception: {str(e)}')
        return render_template('errors/500.html'), 500

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(400)
    def bad_request_error(error):
        if hasattr(error, 'description'):
            app.logger.warning(f"Bad Request: {error.description}")
        return render_template('errors/400.html'), 400

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        app.logger.error(f"HTTP Error {error.code}: {error.description}")
        return render_template(f'errors/{error.code}.html'), error.code

    @app.route("/")
    def index():
        return render_template('index.html')

    return app

if __name__ == "__main__":
    # Démarrage en mode développement (pour debug local)
    application = create_app()
    application.run(host="0.0.0.0", port=8000, debug=True)
