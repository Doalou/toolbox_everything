"""Testeur d'expressions régulières (client-side, RegExp natif)."""

from __future__ import annotations

from flask import Blueprint, render_template

from ._base import Tool, register_tool

TOOL = register_tool(
    Tool(
        slug="regex",
        endpoint="essentials.regex.index",
        title="Testeur de Regex",
        short_title="Regex",
        description="Testez une expression régulière avec highlight des correspondances et capture des groupes.",
        caption="Tester un motif",
        icon="fa-asterisk",
        accent="rose",
        category="developer",
        in_nav=False,
    )
)

bp = Blueprint("regex", __name__, url_prefix="/regex")


@bp.route("/")
def index():
    return render_template("essentials/regex.html", tool=TOOL)
