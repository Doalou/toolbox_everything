"""Decodeur JWT (header + payload, sans vérification de signature)."""

from __future__ import annotations

from flask import Blueprint, render_template

from ._base import Tool, register_tool

TOOL = register_tool(
    Tool(
        slug="jwt",
        endpoint="essentials.jwt.index",
        title="Décodeur JWT",
        short_title="JWT",
        description="Inspectez le header et le payload d'un JSON Web Token. La signature n'est pas vérifiée.",
        caption="Inspecter un token",
        icon="fa-id-card",
        accent="sky",
        category="developer",
        in_nav=False,
    )
)

bp = Blueprint("jwt", __name__, url_prefix="/jwt")


@bp.route("/")
def index():
    return render_template("essentials/jwt.html", tool=TOOL)
