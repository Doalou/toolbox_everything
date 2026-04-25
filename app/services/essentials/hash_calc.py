"""Calculateur de hash (client-side via SubtleCrypto)."""

from __future__ import annotations

from flask import Blueprint, render_template

from ._base import Tool, register_tool

TOOL = register_tool(
    Tool(
        slug="hash",
        endpoint="essentials.hash.index",
        title="Calculateur de hash",
        short_title="Hash",
        description="SHA-1, SHA-256, SHA-384 et SHA-512 calculés localement par votre navigateur.",
        caption="Comparer et vérifier",
        icon="fa-hashtag",
        accent="rose",
        category="encode",
    )
)

bp = Blueprint("hash", __name__, url_prefix="/hash")


@bp.route("/")
def index():
    return render_template("essentials/hash.html", tool=TOOL)
