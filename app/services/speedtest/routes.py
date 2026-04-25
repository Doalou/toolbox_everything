"""
Blueprint Speedtest.

Toolbox embarque LibreSpeed via une iframe. L'URL peut être :

- `LIBRESPEED_URL` : URL interne utilisée pour le healthcheck
  (ex. `http://librespeed` sous Docker).
- `LIBRESPEED_PUBLIC_URL` : URL exposée au navigateur dans l'iframe
  (ex. `http://localhost:8081` ou un sous-domaine public). Par défaut,
  identique à `LIBRESPEED_URL`.
"""

from __future__ import annotations

import requests
from flask import Blueprint, current_app, jsonify, render_template

from app.core.rate_limit import limiter

speedtest_bp = Blueprint("speedtest", __name__, template_folder="../../templates")


def _public_url() -> str:
    cfg = current_app.config
    return (cfg.get("LIBRESPEED_PUBLIC_URL") or cfg.get("LIBRESPEED_URL") or "").rstrip("/")


def _internal_url() -> str:
    return (current_app.config.get("LIBRESPEED_URL") or "").rstrip("/")


@speedtest_bp.route("/")
def index():
    public = _public_url()
    return render_template(
        "speedtest.html",
        librespeed_public_url=public,
        librespeed_configured=bool(public),
    )


@speedtest_bp.route("/status")
@limiter.limit("60 per minute")
def status():
    """Ping rapide de l'instance LibreSpeed (utilisé pour l'UI)."""
    internal = _internal_url()
    if not internal:
        return jsonify({"enabled": False, "reachable": False, "reason": "not_configured"}), 200

    try:
        resp = requests.get(
            internal,
            timeout=3,
            headers={"User-Agent": "Toolbox-Everything"},
        )
        return jsonify({"enabled": True, "reachable": resp.status_code < 500, "status_code": resp.status_code})
    except requests.RequestException as exc:
        return jsonify({"enabled": True, "reachable": False, "reason": str(exc)}), 200
