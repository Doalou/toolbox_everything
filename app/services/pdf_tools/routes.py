"""
Blueprint PDF.

Toolbox n'implémente pas ses propres outils PDF ; on embarque Stirling PDF
(https://github.com/Stirling-Tools/Stirling-PDF) via une iframe. L'URL peut
être :

- `STIRLING_PDF_URL` : URL interne utilisée pour le healthcheck (ex.
  `http://stirling-pdf:8080` sous Docker).
- `STIRLING_PDF_PUBLIC_URL` : URL exposée au navigateur dans l'iframe
  (ex. `http://localhost:8080` ou un sous-domaine public). Par défaut,
  identique à `STIRLING_PDF_URL`.

Si aucune URL n'est définie, on affiche un message expliquant comment
l'activer.
"""

from __future__ import annotations

import requests
from flask import Blueprint, current_app, jsonify, render_template

pdf_bp = Blueprint("pdf", __name__, template_folder="../../templates")


def _public_url() -> str:
    cfg = current_app.config
    return (cfg.get("STIRLING_PDF_PUBLIC_URL") or cfg.get("STIRLING_PDF_URL") or "").rstrip("/")


def _internal_url() -> str:
    return (current_app.config.get("STIRLING_PDF_URL") or "").rstrip("/")


@pdf_bp.route("/")
def index():
    public = _public_url()
    configured = bool(public)
    return render_template(
        "pdf.html",
        stirling_public_url=public,
        stirling_configured=configured,
    )


@pdf_bp.route("/status")
def status():
    """Ping rapide de l'instance Stirling PDF (utilisé pour l'UI)."""
    internal = _internal_url()
    if not internal:
        return jsonify({"enabled": False, "reachable": False, "reason": "not_configured"}), 200

    try:
        resp = requests.get(
            f"{internal}/api/v1/info/status",
            timeout=3,
            headers={"User-Agent": "Toolbox-Everything"},
        )
        if resp.status_code < 500:
            return jsonify({"enabled": True, "reachable": True, "status_code": resp.status_code})
    except requests.RequestException as exc:
        return jsonify({"enabled": True, "reachable": False, "reason": str(exc)}), 200

    # Fallback : ping la racine
    try:
        resp = requests.get(internal, timeout=3)
        return jsonify({"enabled": True, "reachable": resp.status_code < 500, "status_code": resp.status_code})
    except requests.RequestException as exc:
        return jsonify({"enabled": True, "reachable": False, "reason": str(exc)}), 200
