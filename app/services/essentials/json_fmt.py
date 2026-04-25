"""Formateur / validateur / minifier JSON (client-side)."""

from __future__ import annotations

from flask import Blueprint, render_template

from ._base import Tool, register_tool

TOOL = register_tool(
    Tool(
        slug="json",
        endpoint="essentials.json.index",
        title="Formateur JSON",
        short_title="JSON",
        description="Formatez, validez, minifiez du JSON et explorez sa structure.",
        caption="Formater et valider",
        icon="fa-code",
        accent="emerald",
        category="developer",
    )
)

bp = Blueprint("json", __name__, url_prefix="/json")


@bp.route("/")
def index():
    return render_template("essentials/json.html", tool=TOOL)
