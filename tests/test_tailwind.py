"""Tests du pipeline Tailwind Docker/local."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.tailwind import CRITICAL_CLASSES, OUTPUT_CSS, check


def test_tailwind_generated_css_contains_critical_classes():
    css_path = Path(OUTPUT_CSS)
    if not css_path.exists():
        pytest.skip("app/static/css/tailwind.css n'a pas encore ete genere")

    css = css_path.read_text(encoding="utf-8", errors="replace")
    missing = [selector for selector in CRITICAL_CLASSES if selector not in css]
    assert missing == []


def test_tailwind_check_command_accepts_current_generated_css():
    if not Path(OUTPUT_CSS).exists():
        pytest.skip("app/static/css/tailwind.css n'a pas encore ete genere")

    assert check() == 0
