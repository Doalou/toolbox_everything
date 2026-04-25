"""Encodeur / décodeur Base64 (client-side, UTF-8 safe)."""

from __future__ import annotations

from flask import Blueprint, render_template

from ._base import Tool, register_tool

TOOL = register_tool(
    Tool(
        slug="base64",
        endpoint="essentials.base64.index",
        title="Encodeur Base64",
        short_title="Base64",
        description="Encodez et décodez vos données en Base64, avec gestion correcte de l'UTF-8.",
        caption="Encoder ou décoder",
        icon="fa-code",
        accent="amber",
        category="encode",
    )
)

bp = Blueprint("base64", __name__, url_prefix="/base64")


@bp.route("/")
def index():
    return render_template("essentials/base64.html", tool=TOOL)
