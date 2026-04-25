"""Générateur de mots de passe (client-side via crypto.getRandomValues)."""

from __future__ import annotations

from flask import Blueprint, render_template

from ._base import Tool, register_tool

TOOL = register_tool(
    Tool(
        slug="password",
        endpoint="essentials.password.index",
        title="Générateur de mot de passe",
        short_title="Mot de passe",
        description="Mots de passe sécurisés ou passphrases mémorisables, avec analyse de force.",
        caption="Générer plus vite",
        icon="fa-key",
        accent="emerald",
        category="generate",
    )
)

bp = Blueprint("password", __name__, url_prefix="/password")


@bp.route("/")
def index():
    return render_template("essentials/password.html", tool=TOOL)
