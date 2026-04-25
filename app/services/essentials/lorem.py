"""Générateur Lorem Ipsum (client-side)."""

from __future__ import annotations

from flask import Blueprint, render_template

from ._base import Tool, register_tool

TOOL = register_tool(
    Tool(
        slug="lorem",
        endpoint="essentials.lorem.index",
        title="Lorem Ipsum",
        short_title="Lorem",
        description="Générez du texte de remplissage (mots, phrases ou paragraphes).",
        caption="Texte de remplissage",
        icon="fa-align-left",
        accent="amber",
        category="generate",
        in_nav=False,
    )
)

bp = Blueprint("lorem", __name__, url_prefix="/lorem")


@bp.route("/")
def index():
    return render_template("essentials/lorem.html", tool=TOOL)
