"""Rate limiter centralisé (Flask-Limiter).

Une unique instance `limiter` partagée par toute l'application. Elle est
initialisée dans `create_app()` via `limiter.init_app(app)`, puis les
blueprints la consomment via le décorateur `@limiter.limit(...)`.

Storage :
    - prod (Docker) : Redis via `RATELIMIT_STORAGE_URI=redis://redis:6379/0`
      → compteurs partagés entre les workers gunicorn, survivent aux restarts
    - dev local     : fallback `memory://` (compteurs par worker, éphémères)

Clé par défaut : adresse IP du client (respecte `ProxyFix`, donc la
vraie IP est remontée même derrière un reverse proxy).
"""

from __future__ import annotations

import os

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=_STORAGE_URI,
    default_limits=["200 per minute", "2000 per hour"],
    default_limits_exempt_when=lambda: False,
    headers_enabled=True,
    strategy="fixed-window",
    swallow_errors=True,
)
