"""Comparateur de textes (diff ligne par ligne, client-side)."""

from __future__ import annotations

from flask import Blueprint, render_template

from ._base import Tool, register_tool

TOOL = register_tool(
    Tool(
        slug="diff",
        endpoint="essentials.diff.index",
        title="Comparateur de textes",
        short_title="Diff",
        description="Comparez deux textes ligne par ligne et visualisez les différences.",
        caption="Voir les différences",
        icon="fa-code-compare",
        accent="violet",
        category="developer",
        in_nav=False,
    )
)

bp = Blueprint("diff", __name__, url_prefix="/diff")


@bp.route("/")
def index():
    return render_template("essentials/diff.html", tool=TOOL)
