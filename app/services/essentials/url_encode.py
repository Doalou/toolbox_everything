"""Encodeur / décodeur URL (client-side, encodeURIComponent)."""

from __future__ import annotations

from flask import Blueprint, render_template

from ._base import Tool, register_tool

TOOL = register_tool(
    Tool(
        slug="url",
        endpoint="essentials.url.index",
        title="Encodeur URL",
        short_title="URL",
        description="Encodez ou décodez une chaîne pour l'inclure dans une URL (percent-encoding).",
        caption="Percent-encode",
        icon="fa-link",
        accent="sky",
        category="encode",
        in_nav=False,
    )
)

bp = Blueprint("url", __name__, url_prefix="/url-encode")


@bp.route("/")
def index():
    return render_template("essentials/url_encode.html", tool=TOOL)
