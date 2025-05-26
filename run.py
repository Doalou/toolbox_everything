from app.services.main import create_app
from flask_compress import Compress
import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logging(app):
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    file_handler = RotatingFileHandler('logs/toolbox.log', maxBytes=10*1024*1024, backupCount=5)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Toolbox Everything démarré')

app = create_app()
compress = Compress()
compress.init_app(app)

if __name__ == "__main__":
    setup_logging(app)
    app.run(host="0.0.0.0", port=8000, debug=True, threaded=True)
