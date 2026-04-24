"""
Factory Flask de Toolbox Everything.

Tout est initialisé ici pour fonctionner aussi bien sous gunicorn qu'en mode
développement (`python run.py --dev`). La bannière ASCII n'est imprimée qu'une
seule fois (quand `TOOLBOX_PRINT_BANNER=1` — défini par run.py côté dev).
"""

from __future__ import annotations

import logging
import os
import sys
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional

from flask import (Flask, Response, current_app, g, jsonify, redirect,
                   render_template, request, url_for)
from flask_compress import Compress
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix
from yt_dlp.postprocessor import FFmpegPostProcessor

from app import __version__
from app.core.exceptions import register_error_handlers
from config import Config

from .essentials.routes import essentials_bp
from .media_converter.routes import media_bp
from .pdf_tools.routes import pdf_bp
from .youtube_downloader.routes import youtube_bp

DIM = "\033[2m"
RESET = "\033[0m"
BOLD = "\033[1m"
BLUE = "\033[34m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"


def _supports_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _print_banner(app: Flask, ffmpeg_path: Optional[str]) -> None:
    """Bannière ASCII au démarrage (uniquement en dev, jamais sous gunicorn)."""
    use_color = _supports_color()

    def c(code: str, text: str) -> str:
        return f"{code}{text}{RESET}" if use_color else text

    w = 56
    rule = "  " + "-" * w

    def row(label: str, value: str, color: str = CYAN) -> str:
        return f"  |  {label:<18} {c(color, value)}"

    def dot(color: str) -> str:
        return c(color, "*")

    is_dev = app.debug
    mode = "development" if is_dev else "production"
    mode_color = YELLOW if is_dev else GREEN

    host = os.environ.get("HOST", "0.0.0.0")
    port = os.environ.get("PORT", "8000")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "",
        rule,
        "",
        f"     {c(BOLD, 'Toolbox')} {c(BLUE, 'Everything')}",
        f"     {c(DIM, 'v' + __version__ + '  --  ' + now)}",
        "",
        rule,
        "",
        row("mode", f"{dot(mode_color)} {mode}", mode_color),
        row("url", f"http://{host}:{port}"),
        row(
            "python",
            f"{sys.version_info.major}.{sys.version_info.minor}."
            f"{sys.version_info.micro}",
        ),
    ]

    if ffmpeg_path:
        lines.append(row("ffmpeg", f"{dot(GREEN)} {os.path.basename(ffmpeg_path)}", GREEN))
    else:
        lines.append(row("ffmpeg", f"{dot(RED)} manquant", RED))

    stirling_url = os.environ.get("STIRLING_PDF_URL", "").strip()
    if stirling_url:
        lines.append(row("stirling-pdf", f"{dot(GREEN)} {stirling_url}", GREEN))
    else:
        lines.append(row("stirling-pdf", f"{dot(YELLOW)} non configure", YELLOW))

    lines.append(row("uploads", app.config.get("UPLOAD_FOLDER", "-")))
    lines.append("")

    bp_names = sorted(bp.name for bp in app.blueprints.values())
    lines.append(rule)
    lines.append(row("routes", ", ".join(bp_names), DIM))

    if is_dev:
        lines.append("")
        lines.append(
            f"  {c(DIM, '|')}  {c(YELLOW, 'debug')}          "
            f"{c(DIM, 'rechargement auto + logs detailles')}"
        )

    lines.append(rule)
    lines.append("")
    tag = c(GREEN, ">> pret") if not is_dev else c(YELLOW, ">> dev")
    lines.append(f"  {tag}  {c(DIM, f'http://{host}:{port}')}")
    lines.append("")

    print("\n".join(lines), flush=True)


def _configure_logging(app: Flask) -> None:
    """Configure un logging unique (console + fichier avec rotation)."""
    log_dir = os.path.join(app.config["BASE_DIR"], "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "toolbox.log")

    fmt = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    # Évite les doublons si create_app est appelé deux fois (tests)
    if any(
        isinstance(h, RotatingFileHandler) and getattr(h, "baseFilename", "") == log_file
        for h in app.logger.handlers
    ):
        return

    try:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
            delay=True,
        )
        file_handler.setFormatter(fmt)
        file_handler.setLevel(logging.INFO if not app.debug else logging.DEBUG)
        app.logger.addHandler(file_handler)
    except PermissionError:
        # Read-only FS : on se contente du stream handler
        pass

    # En dev ou si Gunicorn est absent, on envoie aussi sur stdout
    if app.debug or not app.logger.handlers:
        stream = logging.StreamHandler(sys.stdout)
        stream.setFormatter(fmt)
        stream.setLevel(logging.DEBUG if app.debug else logging.INFO)
        app.logger.addHandler(stream)

    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)


def create_app(config_class: Optional[object] = None) -> Flask:
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(config_class or Config)
    Config.init_app(app)

    # FFmpeg : une seule source de vérité (config.py)
    ffmpeg_path = Config.get_ffmpeg_path()
    if ffmpeg_path:
        app.config["FFMPEG_PATH"] = ffmpeg_path
        FFmpegPostProcessor._ffmpeg_location.set(ffmpeg_path)

    # Stirling PDF : URL optionnelle pour l'iframe
    app.config["STIRLING_PDF_URL"] = os.environ.get("STIRLING_PDF_URL", "").strip()
    app.config["STIRLING_PDF_PUBLIC_URL"] = os.environ.get(
        "STIRLING_PDF_PUBLIC_URL", app.config["STIRLING_PDF_URL"]
    ).strip()

    # Proxy reverse
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Logging (avant toute chose utilisant app.logger)
    _configure_logging(app)

    # Compression (sous gunicorn aussi)
    Compress(app)

    # Cache-Control pour les statiques
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 60 * 60 * 24 * 7  # 7 jours

    # Blueprints
    app.register_blueprint(youtube_bp, url_prefix="/youtube")
    app.register_blueprint(media_bp, url_prefix="/media")
    app.register_blueprint(essentials_bp, url_prefix="/essentials")
    app.register_blueprint(pdf_bp, url_prefix="/pdf")

    # Gestionnaires d'erreur (JSON pour APIs, HTML pour pages)
    register_error_handlers(app)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/youtube")
    def youtube_redirect():
        return redirect(url_for("youtube.index"))

    @app.route("/essentials")
    def essentials_redirect():
        return redirect(url_for("essentials.index"))

    @app.route("/pdf")
    def pdf_redirect():
        return redirect(url_for("pdf.index"))

    @app.route("/health")
    def health() -> Response:
        """Healthcheck (utilisé par Docker)."""
        import yt_dlp

        status = {
            "status": "ok",
            "version": __version__,
            "yt_dlp": yt_dlp.version.__version__,
            "ffmpeg": bool(app.config.get("FFMPEG_PATH")),
            "stirling_pdf": bool(app.config.get("STIRLING_PDF_URL")),
        }
        return jsonify(status)

    @app.before_request
    def _request_start():
        g.start_time = time.perf_counter()

    @app.after_request
    def _request_end(response: Response) -> Response:
        if request.path.startswith("/static") or request.path == "/health":
            return response
        elapsed = time.perf_counter() - g.get("start_time", time.perf_counter())
        app.logger.info(
            "%s %s -> %s (%.0f ms)",
            request.method,
            request.path,
            response.status_code,
            elapsed * 1000,
        )
        return response

    @app.errorhandler(HTTPException)
    def _handle_http(error: HTTPException):
        # Pour les routes API (/api/..., JSON attendu) → JSON
        accept = request.headers.get("Accept", "")
        if request.path.startswith(("/youtube/", "/media/", "/essentials/api", "/pdf/api")) and "application/json" in accept:
            return (
                jsonify({"error": error.description or error.name, "error_code": error.name.upper().replace(" ", "_")}),
                error.code or 500,
            )

        template = f"errors/{error.code}.html"
        try:
            return render_template(template), error.code or 500
        except Exception:
            return render_template("errors/500.html"), 500

    @app.errorhandler(Exception)
    def _handle_uncaught(error: Exception):
        app.logger.exception("Unhandled exception")
        return render_template("errors/500.html"), 500

    @app.context_processor
    def _inject_globals():
        return {
            "current_year": datetime.now().year,
            "app_version": __version__,
            "stirling_enabled": bool(app.config.get("STIRLING_PDF_URL")),
        }

    # Bannière : uniquement si explicitement demandé (run.py en dev)
    if os.environ.get("TOOLBOX_PRINT_BANNER") == "1":
        _print_banner(app, ffmpeg_path)
        # On évite que les re-créations de l'app (tests, reloader) redessinent tout
        os.environ.pop("TOOLBOX_PRINT_BANNER", None)

    return app


if __name__ == "__main__":
    # Fallback direct (usage rare — préférer run.py)
    create_app().run(host="0.0.0.0", port=8000, debug=True)
