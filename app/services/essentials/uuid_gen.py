"""Générateur d'UUID (v4 aléatoire + v7 ordonné par le temps, côté client)."""

from __future__ import annotations

from flask import Blueprint, render_template

from ._base import Tool, register_tool

TOOL = register_tool(
    Tool(
        slug="uuid",
        endpoint="essentials.uuid.index",
        title="Générateur d'UUID",
        short_title="UUID",
        description="UUID v4 aléatoire et v7 ordonné par le temps, idéal pour les clés primaires.",
        caption="v4 ou v7",
        icon="fa-fingerprint",
        accent="indigo",
        category="developer",
        in_nav=False,
    )
)

bp = Blueprint("uuid", __name__, url_prefix="/uuid")


@bp.route("/")
def index():
    return render_template("essentials/uuid.html", tool=TOOL)
