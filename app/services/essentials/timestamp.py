"""Convertisseur de timestamps (client-side, Intl + Date)."""

from __future__ import annotations

from flask import Blueprint, render_template

from ._base import Tool, register_tool

TOOL = register_tool(
    Tool(
        slug="timestamp",
        endpoint="essentials.timestamp.index",
        title="Convertisseur Timestamp",
        short_title="Timestamp",
        description="Convertissez entre timestamps Unix (sec/ms) et dates ISO 8601, dans n'importe quel fuseau.",
        caption="Timestamp ↔ date",
        icon="fa-clock",
        accent="violet",
        category="developer",
    )
)

bp = Blueprint("timestamp", __name__, url_prefix="/timestamp")


@bp.route("/")
def index():
    return render_template("essentials/timestamp.html", tool=TOOL)
